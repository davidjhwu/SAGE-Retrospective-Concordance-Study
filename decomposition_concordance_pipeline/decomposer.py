"""
Decomposer for Decomposition Concordance Pipeline
"""

import os
from functools import partial
import asyncio
from typing import List, Any, Optional, Dict
import logging

from tqdm import tqdm
import backoff
import requests
from openai import AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion
import nest_asyncio

from .utils import process_claim, chunker
from .api_utils import query_stanford_api

logger = logging.getLogger(__name__)
nest_asyncio.apply()

class MedScoreDecomposer(object):
    def __init__(
            self,
            server_path: str,
            model_name: str,
            prompt_path: Optional[str] = None,
            random_state: int = 42,
            batch_size: int = 32,
            api_key: Optional[str] = None,
            *args,
            **kwargs
    ):
        self.model_name = model_name
        self.random_state = random_state
        self.batch_size = batch_size
        self.system_prompt = None
        self.api_key = api_key
        # Hardcode the prompt path
        prompt_path = 'prompt/decompose_prompt.txt'
        with open(prompt_path) as f:
            self.system_prompt = f.read().strip()

    def __call__(self, decomp_input: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        all_completions = []
        for d in tqdm(decomp_input, desc="Decompose"):
            if self.system_prompt:
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": d['ai_answer']}
                ]
            else:
                messages = [
                    {"role": "user", "content": d['ai_answer']}
                ]
            # Print first 30 characters of user content for debugging
            user_content = messages[1]['content'] if len(messages) > 1 else messages[0]['content']
            print(f"\n=== API CALL (first 30 chars) ===\n{user_content[:30]}...\n================\n")
            response = self.batch_response([messages])[0]
            all_completions.append(response)
        decompositions = self.format_completions(decomp_input, all_completions)
        return decompositions

    def format_completions(self, decomp_input: List[Dict[str, Any]], completions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        import json
        decompositions = []
        claim_counter = 0
        for d_input, completion in zip(decomp_input, completions):
            raw_content = completion['choices'][0]['message']['content']
            claims = []
            try:
                # Remove code block markers if present
                if raw_content.strip().startswith("```"):
                    raw_content = "\n".join(line for line in raw_content.splitlines() if not line.strip().startswith("```") )
                parsed = json.loads(raw_content)
                if isinstance(parsed, dict) and "claims" in parsed:
                    claims = parsed["claims"]
                elif isinstance(parsed, list):
                    claims = parsed
                else:
                    # fallback: treat as a single claim
                    claims = [raw_content.strip()]
            except Exception as e:
                print(f"Warning: Could not parse LLM output as JSON: {e}")
                # fallback to line-based splitting
                claims = process_claim(raw_content.split("\n"))
            for idx, claim in enumerate(claims):
                decomp = {k:v for k,v in d_input.items() if k not in ("context", "id", "ai_answer")}
                decomp["claim"] = claim
                decomp["claim_id"] = idx
                decomp["id"] = str(claim_counter)
                decomp["dav_id"] = d_input["id"]
                decompositions.append(decomp)
                claim_counter += 1
            if not claims:
                decomp = {k:v for k,v in d_input.items() if k not in ("context", "id", "ai_answer")}
                decomp["claim"] = None
                decomp["id"] = str(claim_counter)
                decomp["dav_id"] = d_input["id"]
                decompositions.append(decomp)
                claim_counter += 1
        return decompositions

    def batch_response(self, batch: List[List[Dict[str, str]]]) -> List[Dict[str, Any]]:
        completions = []
        for msg in batch:
            response = query_stanford_api(
                messages=msg,
                api_key=self.api_key,
                model=self.model_name
            )
            completions.append(response)
        return completions
