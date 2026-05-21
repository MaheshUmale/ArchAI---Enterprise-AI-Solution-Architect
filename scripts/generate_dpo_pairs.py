import json
import os
import argparse
import random
import logging
from typing import List, Dict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_dpo_triplets(input_path: str, output_path: str):
    """
    Simulates the generation of (Prompt, Chosen, Rejected) pairs for DPO.
    In a real scenario, we would use a strong judge model to pick the better
    of two student responses, or compare student vs teacher.
    """
    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        dialogues = [json.loads(line) for line in f]

    dpo_dataset = []

    for entry in dialogues:
        convos = entry.get('conversations', [])
        if len(convos) < 2: continue

        prompt = convos[0]['value']
        chosen = convos[1]['value'] # The original teacher response is assumed 'Chosen'

        # Simulating a 'Rejected' response by stripping evidence/justification
        # This helps the model learn that more justification is better.
        rejected = chosen.split('.')[0] + ". This is the recommended approach."

        dpo_dataset.append({
            "prompt": prompt,
            "chosen": chosen,
            "rejected": rejected
        })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in dpo_dataset:
            f.write(json.dumps(item) + "\n")

    logger.info(f"Generated {len(dpo_dataset)} DPO pairs for justification alignment.")
    logger.info(f"Saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate DPO pairs for ArchAI SLM alignment")
    parser.add_argument("--input", type=str, default="backend/data/synthetic_corpus.jsonl")
    parser.add_argument("--output", type=str, default="backend/data/dpo_dataset.jsonl")

    args = parser.parse_args()
    generate_dpo_triplets(args.input, args.output)
