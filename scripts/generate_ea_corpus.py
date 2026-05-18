import os
import sys
import json
import asyncio
import argparse
from typing import List, Dict

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

# Attempt to load LLM from the app environment
try:
    from app.agents.base_agent import get_llm
except ImportError:
    # Fallback to a basic message if get_llm is unavailable
    def get_llm(temperature=0.7):
        class MockLLM:
            async def ainvoke(self, prompt):
                class Resp:
                    content = "FALLBACK: LLM not available in this environment. Please run with proper dependencies."
                return Resp()
        return MockLLM()

class EACorpusGenerator:
    """
    Uses the master index + guidance files to generate high-quality training data
    for SLM distillation (Continued Pre-training and QLoRA).
    """
    def __init__(self, output_file: str):
        self.output_file = output_file
        self.llm = get_llm(temperature=0.8)

    async def generate_examples(self, source_file: str):
        if not os.path.exists(source_file):
            print(f"Source {source_file} not found.")
            return

        with open(source_file, "r") as f:
            content = f.read()

        # Load Guidance/Skills/Guardrails for context
        guidance = ""
        for gf in ["docs/guidance/ARCHAI-GENERIC-GUIDANCE.md", "docs/skills/ARCHAI-GENERIC-SKILLS.md", "docs/guardrails/ARCHAI-GUARDRAILS.md"]:
            if os.path.exists(gf):
                with open(gf, "r") as f:
                    guidance += f"FILE: {gf}\n" + f.read() + "\n---\n"

        prompt = f"""
        You are the ArchAI Synthetic Data Engine.
        Using the following Master EA Sources and Architectural Guidance, generate 2 high-quality,
        multi-turn dialogues in ShareGPT format.

        The dialogues must demonstrate:
        1. Deep architectural reasoning based on the provided sources.
        2. Proper use of skills (e.g., ARCHAI:think-before-architecting, ARCHAI:tradeoff-matrix).
        3. Strict adherence to guardrails (e.g., no hallucinations, bias toward reuse).
        4. Reference to specific official sources found in the index (e.g., TOGAF, BIAN, AWS WAF).
        5. Mermaid diagrams and structured JSON deliverables.

        GUIDANCE & SKILLS:
        {guidance}

        MASTER SOURCES CONTENT (Sample):
        {content[:5000]}

        Output ONLY a JSON list of ShareGPT conversations. Each conversation is an object with a "conversations" key containing a list of {{"from": "human/gpt", "value": "..."}} objects.
        """

        print(f"Generating synthetic corpus from {source_file}...")
        response = await self.llm.ainvoke(prompt)

        if "FALLBACK" in response.content:
            print(response.content)
            return

        try:
            # Basic cleanup of LLM response in case it wraps in markdown blocks
            clean_content = response.content.strip()
            if clean_content.startswith("```json"):
                clean_content = clean_content[7:-3].strip()
            elif clean_content.startswith("```"):
                clean_content = clean_content[3:-3].strip()

            data = json.loads(clean_content)
            if not isinstance(data, list):
                data = [data]

            with open(self.output_file, "a") as f:
                for entry in data:
                    f.write(json.dumps(entry) + "\n")
            print(f"Appended {len(data)} examples to {self.output_file}")
        except Exception as e:
            print(f"Failed to parse LLM response as JSON: {e}")

async def main():
    parser = argparse.ArgumentParser(description="ArchAI EA Corpus Generator")
    parser.add_argument("--input_dir", type=str, default="docs/references")
    parser.add_argument("--output", type=str, default="backend/data/synthetic_corpus.jsonl")
    args = parser.parse_args()

    generator = EACorpusGenerator(args.output)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # Clear output file if it exists to start fresh for this run
    if os.path.exists(args.output):
        os.remove(args.output)

    if os.path.isdir(args.input_dir):
        for filename in os.listdir(args.input_dir):
            if filename.endswith(".md"):
                await generator.generate_examples(os.path.join(args.input_dir, filename))
    else:
        await generator.generate_examples(args.input_dir)

if __name__ == "__main__":
    asyncio.run(main())
