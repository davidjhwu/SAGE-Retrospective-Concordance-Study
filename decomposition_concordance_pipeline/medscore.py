"""
Decomposition Concordance Pipeline main script
"""

import os
import logging
import json
import pandas as pd
from typing import List, Any, Optional, Dict
from argparse import ArgumentParser

import jsonlines
from tqdm import tqdm

from .utils import parse_sentences
from .decomposer import MedScoreDecomposer
from .verifier import ProvidedEvidenceVerifier

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(level=logging.WARNING, format=FORMAT)
logger = logging.getLogger(__name__)

class MedScore(object):
    def __init__(
            self,
            model_name_decomposition: str,
            server_decomposition: str,
            model_name_verification: str,
            server_verification: str,
            response_key: str,
            provided_evidence: Optional[Dict[str, str]] = None,
            prompt_path: Optional[str] = None,
            api_key: Optional[str] = None,
    ):
        self.response_key = response_key
        self.decomposer = MedScoreDecomposer(
            model_name=model_name_decomposition,
            server_path=server_decomposition,
            prompt_path=prompt_path,
            api_key=api_key
        )
        self.verifier = ProvidedEvidenceVerifier(
            model_name=model_name_verification,
            server_path=server_verification,
            id_to_evidence=provided_evidence,
            api_key=api_key
        )

    def decompose(
        self,
        dataset: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        decomposer_input = []
        for item in dataset:
            decomposer_input.append({
                "id": item["id"],
                "ai_answer": item[self.response_key]
            })
        decompositions = self.decomposer(decomposer_input)
        return decompositions

    def verify(self, decompositions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        non_empty_decompositions = [d for d in decompositions if d["claim"] is not None]
        verifier_output = self.verifier(non_empty_decompositions)
        return verifier_output

def load_csv_data(csv_file: str) -> tuple:
    df = pd.read_csv(csv_file, encoding='latin1')
    required_columns = ["dav_id", "ai_answer", "answer", "question"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    dataset = []
    provided_evidence = {}
    for _, row in df.iterrows():
        item_id = str(row["dav_id"])
        ai_answer = str(row["ai_answer"])
        answer = str(row["answer"])
        question = str(row["question"])
        dataset.append({
            "id": item_id,
            "ai_answer": ai_answer
        })
        provided_evidence[item_id] = f"Question: {question}\nReference Answer: {answer}"
    return dataset, provided_evidence

def parse_args():
    parser = ArgumentParser(description="Decomposition Concordance Pipeline")
    parser.add_argument("--input_file", required=True, type=str, help="Path to the input CSV file")
    parser.add_argument("--output_dir", default="./results", type=str, help="Path to output directory")
    parser.add_argument("--prompt_path", type=str, default="prompt/MedScore_prompt.txt", help="Path to the decomposition prompt file")
    parser.add_argument("--api_key", required=True, type=str, help="Stanford API key")
    parser.add_argument("--decompose_only", action="store_true", help="Only run decomposition step")
    parser.add_argument("--verify_only", action="store_true", help="Only run verification step")
    parser.add_argument("--model_name_decomposition", type=str, default="gpt-4", help="Model for decomposition")
    parser.add_argument("--server_decomposition", type=str, default="https://apim.stanfordhealthcare.org/openai20/deployments/gpt-4/chat/completions?api-version=2023-05-15", help="Server for decomposition")
    parser.add_argument("--model_name_verification", type=str, default="gpt-4", help="Model for verification")
    parser.add_argument("--server_verification", type=str, default="https://apim.stanfordhealthcare.org/openai20/deployments/gpt-4/chat/completions?api-version=2023-05-15", help="Server for verification")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)
    print(f"Loading data from {args.input_file}...")
    dataset, provided_evidence = load_csv_data(args.input_file)
    print(f"Loaded {len(dataset)} items from CSV")
    scorer = MedScore(
        model_name_decomposition=args.model_name_decomposition,
        server_decomposition=args.server_decomposition,
        model_name_verification=args.model_name_verification,
        server_verification=args.server_verification,
        response_key="ai_answer",
        provided_evidence=provided_evidence,
        prompt_path=args.prompt_path,
        api_key=args.api_key
    )
    decomp_output_file = os.path.join(args.output_dir, "decompositions.jsonl")
    verif_output_file = os.path.join(args.output_dir, "verifications.jsonl")
    output_file = os.path.join(args.output_dir, "final_output.jsonl")
    if not args.verify_only:
        print("Running decomposition...")
        decompositions = scorer.decompose(dataset)
        # Reformat decompositions for output
        formatted_decompositions = []
        for d in decompositions:
            formatted = {
                'dav_id': d.get('dav_id'),
                'claim_id': d.get('claim_id'),
                'id': d.get('id'),
                'claim': d.get('claim')
            }
            formatted_decompositions.append(formatted)
        with jsonlines.open(decomp_output_file, 'w') as writer:
            writer.write_all(formatted_decompositions)
        print(f"Saved {len(decompositions)} decompositions to {decomp_output_file}")
        if args.decompose_only:
            print("Decomposition complete. Exiting.")
            exit(0)
    if args.verify_only:
        print(f"Loading decompositions from {decomp_output_file}...")
        with jsonlines.open(decomp_output_file, 'r') as reader:
            decompositions = [item for item in reader.iter()]
    print("Running verification...")
    verifications = scorer.verify(decompositions)
    with jsonlines.open(verif_output_file, 'w') as writer:
        # Reformat verifications for output
        formatted_verifications = []
        for v in verifications:
            formatted = {
                'dav_id': v.get('dav_id'),
                'claim_id': v.get('claim_id'),
                'id': v.get('id'),
                'claim': v.get('claim'),
                'evidence': (v.get('reference', '')[:20] + '...') if v.get('reference') else '',
                'score': v.get('score'),
                'reason': v.get('reason')
            }
            formatted_verifications.append(formatted)
        writer.write_all(formatted_verifications)
    print(f"Saved {len(verifications)} verifications to {verif_output_file}")
    print("Combining results...")
    # Build a mapping from dav_id to counts of each score
    david_counts = {}
    for verif in verifications:
        dav_id = verif.get('dav_id')
        score = verif.get('score')
        if dav_id is None or score is None:
            continue
        if dav_id not in david_counts:
            david_counts[dav_id] = {'Supported': 0, 'Not Supported': 0, 'Not Addressed': 0}
        if score in david_counts[dav_id]:
            david_counts[dav_id][score] += 1
    # Prepare output as a list of dicts
    summary_output = []
    for dav_id, counts in david_counts.items():
        entry = {'dav_id': dav_id}
        entry.update(counts)
        supported = counts['Supported']
        not_supported = counts['Not Supported']
        not_addressed = counts['Not Addressed']
        total = supported + not_supported + not_addressed
        support_denom = supported + not_supported
        # Report as 'numerator/denominator' strings
        entry['support_fraction'] = f"{supported}/{support_denom}" if support_denom > 0 else "0/0"
        entry['support_percentage'] = f"{supported/support_denom*100}%" if support_denom > 0 else "0%"
        entry['not_addressed_fraction'] = f"{not_addressed}/{total}" if total > 0 else "0/0"
        entry['not_addressed_percentage'] = f"{not_addressed/total*100}%" if total > 0 else "0%"
        summary_output.append(entry)
    with jsonlines.open(output_file, 'w') as writer:
        writer.write_all(summary_output)
    print(f"Saved final results to {output_file}")
    print("Pipeline complete!") 