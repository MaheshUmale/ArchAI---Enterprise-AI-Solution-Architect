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
                    # Provide a realistic sample if dependencies are missing
                    content = json.dumps([{
                        "conversations": [
                            {"from": "human", "value": "How should I design a multi-region data architecture on AWS?"},
                            {"from": "gpt", "value": "According to the AWS Well-Architected Framework and DDIA principles, you should first consider the trade-offs between latency, cost, and consistency. ARCHAI:think-before-architecting suggests exploring active-active vs active-passive patterns... [Synthetic Response]"}
                        ]
                    }])
                return Resp()
        return MockLLM()

class EACorpusGenerator:
    """
    Uses the master index + guidance files to generate high-quality training data
    for SLM distillation (Continued Pre-training and QLoRA).
    """
    def __init__(self, output_file: str):
        self.output_file = output_file
        try:
            self.llm = get_llm(temperature=0.8)
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            sys.exit(1)

    def load_guidance(self) -> str:
        guidance = ""
        guidance_paths = [
            "docs/guidance/ARCHAI-GENERIC-GUIDANCE.md",
            "docs/skills/ARCHAI-GENERIC-SKILLS.md",
            "docs/guardrails/ARCHAI-GUARDRAILS.md"
        ]
        for gf in guidance_paths:
            full_path = os.path.join(BASE_DIR, gf)
            if os.path.exists(full_path):
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        guidance += f"--- FILE: {gf} ---\n" + f.read() + "\n\n"
                except Exception as e:
                    logger.warning(f"Failed to read guidance file {gf}: {e}")
        return guidance

    async def generate_examples(self, source_file: str, num_examples: int = 2):
        if not os.path.exists(source_file):
            logger.error(f"Source file {source_file} not found.")
            return

        logger.info(f"Generating synthetic corpus from {source_file}...")
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read source file {source_file}: {e}")
            return

        guidance = self.load_guidance()

        prompt = f"""
        You are the ArchAI Synthetic Data Engine.
        Using the following Master EA Sources and Architectural Guidance, generate {num_examples} high-quality,
        multi-turn dialogues in ShareGPT format.

        The dialogues must demonstrate:
        1. Deep architectural reasoning based on the provided sources.
        2. Proper use of ArchAI skills (e.g., ARCHAI:think-before-architecting, ARCHAI:tradeoff-matrix).
        3. Strict adherence to ArchAI guardrails (e.g., no hallucinations, bias toward reuse).
        4. Reference to specific official sources found in the index (e.g., TOGAF, BIAN, AWS WAF).
        5. Mermaid diagrams and structured JSON deliverables.

        --- ARCHAI GUIDANCE & SKILLS ---
        {guidance}

        --- MASTER SOURCES CONTENT (Context) ---
        {content[:6000]}

        Output ONLY a JSON list of objects. Each object represents one conversation and must have a "conversations" key containing a list of {{"from": "human/gpt", "value": "..."}} objects.
        """

        response = await self.llm.ainvoke(prompt)

        try:
            # Clean the response content
            clean_content = response.content.strip()
            if clean_content.startswith("```json"):
                clean_content = clean_content[7:-3].strip()
            elif clean_content.startswith("```"):
                clean_content = clean_content[3:-3].strip()

            data = json.loads(clean_content)
            if not isinstance(data, list):
                data = [data]

            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            with open(self.output_file, "a", encoding="utf-8") as f:
                for entry in data:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            logger.info(f"Appended {len(data)} examples to {self.output_file}")
        except Exception as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Raw Response: {response.content}")

async def main():
    parser = argparse.ArgumentParser(description="ArchAI EA Corpus Generator for SLM Distillation")
    parser.add_argument(
        "--input_dir",
        type=str,
        default="docs/references",
        help="Directory containing source markdown files"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="backend/data/synthetic_corpus.jsonl",
        help="Path to the output JSONL file"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=2,
        help="Number of examples to generate per file"
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to output file instead of overwriting"
    )

    args = parser.parse_args()

    generator = EACorpusGenerator(args.output)

    # Handle file management
    if not args.append and os.path.exists(args.output):
        logger.info(f"Overwriting existing output file: {args.output}")
        os.remove(args.output)

    source_path = os.path.join(BASE_DIR, args.input_dir)
    if os.path.isdir(source_path):
        for filename in os.listdir(source_path):
            if filename.endswith(".md"):
                await generator.generate_examples(os.path.join(source_path, filename), args.count)
    elif os.path.isfile(source_path):
        await generator.generate_examples(source_path, args.count)
    else:
        logger.error(f"Input path not found: {source_path}")

if __name__ == "__main__":
    asyncio.run(main())
