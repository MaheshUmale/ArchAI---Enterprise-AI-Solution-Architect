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
    """Loads dialogue data in ShareGPT format from JSON or JSONL."""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return []

    try:
        if file_path.endswith('.jsonl'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return [json.loads(line) for line in f]
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else [data]
    except Exception as e:
        logger.error(f"Failed to load {file_path}: {e}")
        return []

def extract_assistant_responses(dialogues: List[Dict]) -> List[str]:
    """Extracts assistant responses to judge domain skill uniqueness."""
    corpus = []
    for entry in dialogues:
        convos = entry.get('conversations', [])
        assistant_turns = [turn['value'] for turn in convos if turn.get('from') == 'gpt']
        # Join turns to represent the assistant's full contribution to the dialogue
        corpus.append(" ".join(assistant_turns))
    return corpus

def filter_by_diversity(input_path: str, output_path: str, model_name: str, threshold: float):
    try:
        from sentence_transformers import SentenceTransformer
        import torch
    except ImportError:
        logger.error("Dependencies missing. Please install sentence-transformers and torch.")
        logger.info("Try running: pip install -r scripts/requirements_slm.txt")
        return

    logger.info(f"Loading local embedding model: {model_name}")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(model_name, device=device)

    dialogues = load_data(input_path)
    if not dialogues:
        return

    text_corpus = extract_assistant_responses(dialogues)

    logger.info(f"Encoding {len(text_corpus)} dialogues on {device}...")
    embeddings = model.encode(text_corpus, convert_to_tensor=True, show_progress_bar=True)

    logger.info("Computing pairwise cosine similarity...")
    similarity_matrix = model.similarity(embeddings, embeddings)

    indices_to_remove = set()
    num_samples = len(text_corpus)

    for i in range(num_samples):
        if i in indices_to_remove:
            continue
        for j in range(i + 1, num_samples):
            if similarity_matrix[i][j] > threshold:
                indices_to_remove.add(j)

    clean_dialogues = [dialogues[idx] for idx in range(num_samples) if idx not in indices_to_remove]

    logger.info(f"--- Diversity Optimization Report ---")
    logger.info(f"Original Count: {num_samples}")
    logger.info(f"Removed Redundant: {len(indices_to_remove)}")
    logger.info(f"Optimized Count: {len(clean_dialogues)}")
    logger.info(f"Retained: {(len(clean_dialogues)/num_samples)*100:.2f}%")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Save as JSON for clean portability
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(clean_dialogues, f, indent=4)
    logger.info(f"Cleaned corpus saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Local Diversity Filtering for ArchAI SLM Distillation")
    parser.add_argument("--input", type=str, default="backend/data/synthetic_corpus.jsonl", help="Input JSON or JSONL file")
    parser.add_argument("--output", type=str, default="backend/data/synthetic_corpus_optimized.json", help="Output JSON file")
    parser.add_argument("--model", type=str, default="sentence-transformers/all-MiniLM-L6-v2", help="SentenceTransformer model name")
    parser.add_argument("--threshold", type=float, default=0.85, help="Cosine similarity threshold (0.0 - 1.0)")

    args = parser.parse_args()
    filter_by_diversity(args.input, args.output, args.model, args.threshold)
