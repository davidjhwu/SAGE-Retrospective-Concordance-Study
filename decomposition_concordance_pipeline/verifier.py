"""Verifier for Decomposition Concordance Pipeline"""

import os
import asyncio
import json
import pathlib
from typing import List, Dict, Any, Optional

from tqdm import tqdm
import nest_asyncio
import inspect

from .utils import chunker
from .api_utils import query_stanford_api

nest_asyncio.apply()

class ProvidedEvidenceVerifier(object):
    """
    Verifies claims against reference evidence using an LLM API.
    """
    def __init__(
            self,
            server_path: str,
            model_name: str,
            id_to_evidence: Dict[str, str],
            random_state: int = 42,
            batch_size: int = 32,
            api_key: Optional[str] = None,
            prompt_path: Optional[str] = None,
            **kwargs,
    ):
        self.model_name = model_name
        self.id_to_evidence = id_to_evidence
        self.random_state = random_state
        self.batch_size = batch_size
        self.api_key = api_key
        if prompt_path is None:
            prompt_path = os.path.join(pathlib.Path(__file__).parent.parent, 'prompt', 'verifier_prompt.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.prompt_template = f.read()

    def __call__(self, decompositions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Group decompositions by dav_id
        grouped = {}
        for d in decompositions:
            dav_id = d['dav_id']
            if dav_id not in grouped:
                grouped[dav_id] = []
            grouped[dav_id].append(d)
        verification_output = []
        for dav_id, claims in tqdm(grouped.items(), desc="Verify"):
            reference = self.id_to_evidence[dav_id]
            claim_texts = [c['claim'] for c in claims]
            all_verdicts = []
            for claim_chunk in chunker(claim_texts, 10):  # batch size 10
                prompt = self.format_batched_prompt(reference, claim_chunk)
                messages = [{"role": "user", "content": prompt}]
                response = self.batch_response([messages])[0]
                raw_output = inspect.cleandoc(response['choices'][0]['message']['content'])
                #print(f"Prompt length (chars): {len(prompt)}")
                #print(f"=== LLM RAW OUTPUT for dav_id: {dav_id} ===\n{raw_output}\n==============================\n")
                # Robust parsing logic (removes code block markers, flexible JSON parsing, fallback)
                if raw_output.strip().startswith("```"):
                    raw_output = "\n".join(
                        line for line in raw_output.splitlines() if not line.strip().startswith("```")
                    ).strip()
                raw_output = inspect.cleandoc(raw_output)
                try:
                    verdicts = json.loads(raw_output)
                    if isinstance(verdicts, dict):
                        verdicts = [verdicts for _ in range(len(claim_chunk))]
                    print(f"dav_id: {dav_id} | Claims sent: {len(claim_chunk)} | Verdicts received (LLM): {len(verdicts)}")
                    if not isinstance(verdicts, list) or len(verdicts) != len(claim_chunk):
                        raise ValueError("Output JSON does not match number of claims")
                except Exception as e:
                    print(f"Parse error: {e}\nRaw output was:\n{raw_output}")
                    verdicts = [{"verdict": "Not Supported", "reason": f"Parse error: {e}"} for _ in range(len(claim_chunk))]
                all_verdicts.extend(verdicts)
            print(f"dav_id: {dav_id} | Total claims sent: {len(claim_texts)} | Total verdicts received: {len(all_verdicts)}")
            for c, v in zip(claims, all_verdicts):
                output = {k: v for k, v in c.items()}
                output["raw"] = raw_output
                output["score"] = v.get("verdict", "")
                output["reason"] = v.get("reason", "")
                output["reference"] = reference
                verification_output.append(output)
        return verification_output

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

    def format_batched_prompt(self, reference: str, claims: list) -> str:
        prompt = self.prompt_template.format(
            reference=json.dumps(reference),
            claims=json.dumps(claims, ensure_ascii=False)
        )
        return prompt
