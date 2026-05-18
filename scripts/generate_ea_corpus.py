import os
import sys
import json
import asyncio
import logging
import argparse
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
    Uses the master index + processed docs + guidance files to generate high-quality
    training data for SLM distillation in ShareGPT format.
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

    async def generate_examples(self, context_content: str, source_name: str, num_examples: int = 2):
        guidance = self.load_guidance()

        prompt = f"""
        You are the ArchAI Synthetic Data Engine.
        Your task is to generate {num_examples} extremely high-quality, multi-turn architectural dialogues between a Human and ArchAI (the GPT assistant).

        The dialogues must be in ShareGPT format.

        --- REQUIREMENTS ---
        1. ASSISTANT ROLE: ArchAI is an expert Enterprise Architect. It must be professional, evidence-based, and surgical.
        2. SKILLS: ArchAI MUST use specific skills:
           - ARCHAI:think-before-architecting (internal monologue about trade-offs)
           - ARCHAI:tradeoff-matrix (structured comparison)
           - ARCHAI:reuse-first (evaluating existing assets)
        3. SOURCE GROUNDING: Base the technical advice on the provided context: {source_name}.
        4. COMPLEXITY: Human should ask complex, multi-layered enterprise questions (e.g., legacy migration, global scale, data mesh).
        5. FORMAT: Output ONLY a JSON list of objects. Each object has a "conversations" key.
           Example:
           [
             {{
               "conversations": [
                 {{"from": "human", "value": "..."}},
                 {{"from": "gpt", "value": "..."}},
                 {{"from": "human", "value": "..."}},
                 {{"from": "gpt", "value": "..."}}
               ]
             }}
           ]

        --- ARCHAI GUIDANCE & SKILLS ---
        {guidance}

        --- CONTEXT CONTENT ({source_name}) ---
        {context_content[:8000]}

        Output ONLY valid JSON.
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
            logger.info(f"Appended {len(data)} examples from {source_name} to {self.output_file}")
        except Exception as e:
            logger.error(f"Failed to parse LLM response as JSON from {source_name}: {e}")
            # logger.debug(f"Raw Response: {response.content}")

async def main():
    parser = argparse.ArgumentParser(description="ArchAI EA Corpus Generator for SLM Distillation")
    parser.add_argument(
        "--master_sources",
        type=str,
        default="backend/data/master_sources.json",
        help="Path to master sources JSON"
    )
    parser.add_argument(
        "--processed_docs",
        type=str,
        default="backend/data/processed_docs.json",
        help="Path to processed docs JSON"
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
        help="Number of examples to generate per source"
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

    # 1. Process Master Index Sources
    if os.path.exists(args.master_sources):
        with open(args.master_sources, "r", encoding="utf-8") as f:
            sources = json.load(f)
            # Pick a sample if too many, or process all.
            # For demonstration, we'll take a few.
            sample_sources = random.sample(sources, min(len(sources), 5))
            for src in sample_sources:
                content = f"Title: {src['title']}\nTopic: {src['topic']}\nDescription: {src['description']}\nURL: {src['url']}"
                await generator.generate_examples(content, src['title'], args.count)

    # 2. Process Large Documents
    if os.path.exists(args.processed_docs):
        with open(args.processed_docs, "r", encoding="utf-8") as f:
            docs = json.load(f)
            # Pick a few documents to process
            sample_docs = random.sample(docs, min(len(docs), 3))
            for doc in sample_docs:
                # Take a random chunk if doc is very large
                content = doc['content']
                if len(content) > 10000:
                    start = random.randint(0, len(content) - 10000)
                    content = content[start:start+10000]
                await generator.generate_examples(content, doc['filename'], args.count)

if __name__ == "__main__":
    asyncio.run(main())
