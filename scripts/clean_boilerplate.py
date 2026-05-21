import json
import os
import argparse
import re
import logging
from typing import List, Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# List of common teacher LLM "phrasing traps" or boilerplate to remove
BOILERPLATE_PATTERNS = [
    r"^As an? (Enterprise|Solution|System|Lead) Architect, I (recommend|suggest|would say)...?",
    r"^Certainly! I can help you with that.",
    r"^Here is a detailed architectural design...",
    r"^I understand your requirements.",
    r"^Let's dive into the architectural details.",
    r"Let me know if you need anything else\.",
    r"I hope this helps!",
    r"^Great question\.",
    r"^To address your concerns regarding",
    r"Please note that this is a high-level overview\."
]

def clean_text(text: str) -> str:
    """Removes boilerplate patterns from the beginning or end of the text."""
    cleaned = text.strip()
    for pattern in BOILERPLATE_PATTERNS:
        # Remove patterns at the beginning (case-insensitive)
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()
    return cleaned

def clean_dialogues(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        if input_path.endswith('.jsonl'):
            dialogues = [json.loads(line) for line in f]
        else:
            dialogues = json.load(f)

    cleaned_count = 0
    for entry in dialogues:
        convos = entry.get('conversations', [])
        for turn in convos:
            if turn.get('from') == 'gpt':
                original_value = turn['value']
                cleaned_value = clean_text(original_value)
                if original_value != cleaned_value:
                    turn['value'] = cleaned_value
                    cleaned_count += 1

    # Save the cleaned dialogues
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dialogues, f, indent=4)

    logger.info(f"Boilerplate Removal Report:")
    logger.info(f"Total Dialogues Processed: {len(dialogues)}")
    logger.info(f"GPT Turns Cleaned: {cleaned_count}")
    logger.info(f"Cleaned corpus saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean systemic boilerplate from ArchAI synthetic corpus")
    parser.add_argument("--input", type=str, default="backend/data/synthetic_corpus_optimized.json", help="Input JSON file")
    parser.add_argument("--output", type=str, default="backend/data/synthetic_corpus_cleaned.json", help="Output JSON file")

    args = parser.parse_args()
    clean_dialogues(args.input, args.output)
