import json
import os
import argparse
import logging
from typing import List, Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_data(file_path: str) -> List[Dict]:
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.endswith('.jsonl'):
                return [json.loads(line) for line in f]
            else:
                data = json.load(f)
                return data if isinstance(data, list) else [data]
    except Exception as e:
        logger.error(f"Failed to load {file_path}: {e}")
        return []

def precheck_tokenization(input_path: str, model_id: str, max_seq_length: int):
    try:
        from transformers import AutoTokenizer
    except ImportError:
        logger.error("Transformers library missing. Please install it.")
        logger.info("Try running: pip install -r scripts/requirements_slm.txt")
        return

    logger.info(f"Loading tokenizer for: {model_id}")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    except Exception as e:
        logger.error(f"Failed to load tokenizer: {e}")
        return

    dialogues = load_data(input_path)
    if not dialogues:
        return

    logger.info(f"Checking {len(dialogues)} dialogues against max_seq_length={max_seq_length}")

    too_long = 0
    format_errors = 0
    total_tokens = 0
    unescaped_chars = 0
    broken_sequences = 0

    for idx, entry in enumerate(dialogues):
        convos = entry.get('conversations', [])
        if not convos:
            logger.warning(f"Sample {idx} has no conversations.")
            format_errors += 1
            continue

        # Multi-turn sequence check (should ideally start with human and alternate)
        if len(convos) < 2:
            logger.warning(f"Sample {idx} is not multi-turn (only {len(convos)} turns).")
            broken_sequences += 1

        # Basic ShareGPT format check
        for turn_idx, turn in enumerate(convos):
            if 'from' not in turn or 'value' not in turn:
                logger.warning(f"Sample {idx} turn {turn_idx} has invalid format: {turn}")
                format_errors += 1
                continue

            val = turn['value']
            if not val or val.strip() == "":
                logger.warning(f"Sample {idx} turn {turn_idx} has empty content.")
                format_errors += 1

            # Check for common unescaped character issues that might break JSON/tokenization
            # Specifically looking for control characters or broken unicode
            if any(ord(c) < 32 and c not in '\n\r\t' for c in val):
                 logger.warning(f"Sample {idx} turn {turn_idx} contains unescaped control characters.")
                 unescaped_chars += 1

        # Phi-3 Chat Template (simulated if template not available, but ideally use tokenizer.apply_chat_template)
        try:
            # Most modern tokenizers have a chat template
            if hasattr(tokenizer, "apply_chat_template"):
                # We need to map ShareGPT ('from', 'value') to ('role', 'content')
                mapped_conv = []
                for turn in convos:
                    role = "user" if turn['from'] == "human" else "assistant"
                    mapped_conv.append({"role": role, "content": turn['value']})

                full_text = tokenizer.apply_chat_template(mapped_conv, tokenize=False)
                tokens = tokenizer.encode(full_text)
            else:
                # Fallback to raw concatenation
                full_text = " ".join([t['value'] for t in convos])
                tokens = tokenizer.encode(full_text)

            total_tokens += len(tokens)
            if len(tokens) > max_seq_length:
                too_long += 1
                logger.debug(f"Sample {idx} is too long: {len(tokens)} tokens")
        except Exception as e:
            logger.error(f"Error processing sample {idx}: {e}")
            format_errors += 1

    logger.info(f"--- Tokenization Pre-check Report ---")
    logger.info(f"Total Samples: {len(dialogues)}")
    logger.info(f"Avg Tokens/Sample: {total_tokens/len(dialogues) if dialogues else 0:.2f}")
    logger.info(f"Samples exceeding {max_seq_length}: {too_long} ({(too_long/len(dialogues))*100 if dialogues else 0:.2f}%)")
    logger.info(f"Format Errors: {format_errors}")
    logger.info(f"Broken Multi-turn Sequences: {broken_sequences}")
    logger.info(f"Unescaped Control Characters: {unescaped_chars}")

    if too_long > 0 or format_errors > 0 or broken_sequences > 0 or unescaped_chars > 0:
        logger.warning("Action suggested: Trim long dialogues or fix format/sequence errors before training.")
    else:
        logger.info("Dataset passed tokenization pre-check!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Local Tokenization Pre-check for ArchAI SLM Distillation")
    parser.add_argument("--input", type=str, default="backend/data/synthetic_corpus_optimized.json", help="Input JSON or JSONL file")
    parser.add_argument("--model", type=str, default="microsoft/Phi-3.5-mini-instruct", help="HF Model ID for tokenizer")
    parser.add_argument("--max_length", type=int, default=2048, help="Target max sequence length")

    args = parser.parse_args()
    precheck_tokenization(args.input, args.model, args.max_length)
