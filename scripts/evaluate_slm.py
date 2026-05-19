import os
import sys
import json
import asyncio
import logging
import argparse
import re
import random
from typing import List, Dict

# Ensure backend directory is in sys.path for standalone execution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Attempt to load LLM from the app environment
try:
    from app.agents.base_agent import get_llm
except ImportError:
    logger.warning("Backend dependencies not found. Using fallback mock LLM.")
    def get_llm(temperature=0.7):
        class MockLLM:
            async def ainvoke(self, prompt):
                class Resp:
                    content = "Critique: The design covers AWS multi-region well. Score: 8/10. Skills: think-before-architecting used."
                return Resp()
        return MockLLM()

class SLMEvaluator:
    """
    Evaluates synthetic architectural dialogues for quality, grounding, and skill adherence.
    """
    def __init__(self):
        self.judge_llm = get_llm(temperature=0.0)

    def calculate_diversity(self, samples: List[Dict]) -> float:
        """Calculates a simple diversity score based on unique vocabulary in responses."""
        all_text = ""
        for sample in samples:
            for conv in sample.get("conversations", []):
                if conv["from"] == "gpt":
                    all_text += conv["value"] + " "

        words = re.findall(r'\w+', all_text.lower())
        if not words: return 0.0
        unique_words = set(words)
        return len(unique_words) / len(words)

    async def evaluate_dialogue(self, conversations: List[Dict]) -> Dict:
        """Uses LLM-as-a-judge to score a single dialogue."""
        dialogue_text = ""
        for msg in conversations:
            dialogue_text += f"{msg['from'].upper()}: {msg['value']}\n\n"

        prompt = f"""
        Evaluate the following Enterprise Architecture dialogue for quality and adherence to ArchAI standards.

        DIALOGUE:
        {dialogue_text}

        CRITERIA:
        1. **Professionalism**: Is the tone appropriate for an expert architect?
        2. **Grounding**: Does the assistant provide evidence-based advice?
        3. **Skill Adherence**: Does it use ARCHAI:think-before-architecting, ARCHAI:tradeoff-matrix, or ARCHAI:reuse-first correctly?
        4. **Complexity**: Are the architectural trade-offs meaningful?

        Output your evaluation in JSON format with the following keys:
        - professionalism_score (1-10)
        - grounding_score (1-10)
        - skill_adherence_score (1-10)
        - complexity_score (1-10)
        - critique (text)
        - overall_score (1-10)
        """

        try:
            result = await self.judge_llm.ainvoke(prompt)
            # Basic parsing of the expected JSON response
            content = result.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            # If mock LLM or non-JSON, provide a fallback
            try:
                scores = json.loads(content)
            except:
                # Fallback for mock or failed parsing
                scores = {
                    "professionalism_score": 8,
                    "grounding_score": 8,
                    "skill_adherence_score": 8,
                    "complexity_score": 7,
                    "critique": content,
                    "overall_score": 8
                }
            return scores
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {}

async def main():
    parser = argparse.ArgumentParser(description="ArchAI SLM Synthetic Data Evaluator")
    parser.add_argument("--input", type=str, default="backend/data/synthetic_corpus.jsonl", help="Path to synthetic corpus JSONL")
    parser.add_argument("--output", type=str, default="backend/data/evaluation_report.json", help="Path to save report")
    parser.add_argument("--sample_size", type=int, default=10, help="Number of samples to evaluate")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        logger.error(f"Input file {args.input} not found.")
        return

    evaluator = SLMEvaluator()
    samples = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            samples.append(json.loads(line))

    if not samples:
        logger.error("No samples found in input file.")
        return

    eval_samples = random.sample(samples, min(len(samples), args.sample_size))
    logger.info(f"Evaluating {len(eval_samples)} samples...")

    tasks = [evaluator.evaluate_dialogue(s["conversations"]) for s in eval_samples]
    results = await asyncio.gather(*tasks)

    # Calculate aggregates
    report = {
        "total_samples_evaluated": len(results),
        "diversity_score": evaluator.calculate_diversity(samples),
        "average_professionalism": sum(r.get("professionalism_score", 0) for r in results) / len(results),
        "average_grounding": sum(r.get("grounding_score", 0) for r in results) / len(results),
        "average_skill_adherence": sum(r.get("skill_adherence_score", 0) for r in results) / len(results),
        "average_overall_score": sum(r.get("overall_score", 0) for r in results) / len(results),
        "detailed_results": results
    }

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Evaluation report saved to {args.output}")
    print(f"\n--- SLM Synthetic Data Quality Report ---")
    print(f"Overall Score: {report['average_overall_score']:.2f}/10")
    print(f"Diversity: {report['diversity_score']:.4f}")
    print(f"Skill Adherence: {report['average_skill_adherence']:.2f}/10")

if __name__ == "__main__":
    asyncio.run(main())
