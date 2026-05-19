import os
import sys
import json
import asyncio
import logging
import argparse
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
                    content = "The model response is excellent, follow the ArchAI philosophy perfectly. Score: 9/10."
                return Resp()
        return MockLLM()

class SLMEvaluator:
    """
    Evaluates SLM generated architectural designs against ground truth or using LLM-as-a-judge.
    """
    def __init__(self):
        self.judge_llm = get_llm(temperature=0.0)

    async def evaluate_sample(self, question: str, response: str, context: str = "") -> Dict:
        prompt = f"""
        Evaluate the following architectural response from an AI Solution Architect (ArchAI).

        Question: {question}
        Response: {response}
        Context: {context}

        CRITERIA:
        1. Professionalism and Tone.
        2. Evidence-based reasoning (does it use provided context?).
        3. Use of ArchAI skills (think-before-architecting, tradeoff-matrix, reuse-first).
        4. Correctness and Feasibility.

        Provide a brief critique and a score out of 10.
        """

        result = await self.judge_llm.ainvoke(prompt)
        return {
            "critique": result.content,
            "question": question
        }

async def main():
    parser = argparse.ArgumentParser(description="ArchAI SLM Evaluator (LLM-as-a-Judge)")
    parser.add_argument("--input", type=str, help="Path to a JSONL file with model outputs to evaluate")
    parser.add_argument("--output", type=str, default="backend/data/evaluation_results.json", help="Path to save results")

    args = parser.parse_args()

    evaluator = SLMEvaluator()
    results = []

    if args.input and os.path.exists(args.input):
        with open(args.input, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                # Assuming input format: {"question": "...", "response": "..."}
                res = await evaluator.evaluate_sample(data.get("question", ""), data.get("response", ""))
                results.append(res)

        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Evaluation complete. Results saved to {args.output}")
    else:
        logger.info("No input file provided for evaluation. Skeleton ready.")

if __name__ == "__main__":
    asyncio.run(main())
