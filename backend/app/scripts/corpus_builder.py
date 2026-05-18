import json
import os
import asyncio
import argparse
from typing import List, Dict
from app.agents.base_agent import get_llm
from app.core.config import settings

class CorpusBuilder:
    """
    Synthesizes high-quality EA training data from knowledge base assets.
    Implements the philosophy of smart curation for SLM distillation.
    """
    def __init__(self, output_file: str = "backend/data/synthetic_corpus.jsonl"):
        self.llm = get_llm(temperature=0.7)
        self.output_path = output_file
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

    async def generate_synthetic_dialogue(self, source_content: str) -> Dict:
        """
        Converts raw EA content into a multi-turn agentic dialogue.
        """
        prompt = f"""
        You are the ArchAI Teacher Model. Use the provided Enterprise Architecture content to generate
        a high-quality, multi-turn dialogue between a user and the ArchAI multi-agent system.

        The dialogue should involve multiple specialist agents:
        - Orchestrator (Project Lead)
        - Knowledge (Retrieval)
        - Reuse & Compliance (Guardrails)
        - Trade-off & Cost (Analysis)
        - Design (Mermaid/Diagrams)
        - Reviewer (QA)

        Input Content:
        {source_content}

        Output format: ShareGPT (conversations list with 'from' and 'value').
        Ensure the output includes trade-off reasoning, Mermaid diagrams, and compliance checks.
        Return ONLY the JSON.
        """

        response = await self.llm.ainvoke(prompt)
        try:
            return json.loads(response.content)
        except:
            return {"raw_response": response.content}

    def save_to_corpus(self, data: Dict):
        with open(self.output_path, "a") as f:
            f.write(json.dumps(data) + "\n")

    async def process_directory(self, input_dir: str):
        """Scans directory and generates dialogues for all found files."""
        for filename in os.listdir(input_dir):
            if filename.endswith(".md") or filename.endswith(".txt"):
                filepath = os.path.join(input_dir, filename)
                with open(filepath, "r") as f:
                    content = f.read()
                print(f"Processing {filename}...")
                dialogue = await self.generate_synthetic_dialogue(content)
                self.save_to_corpus(dialogue)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ArchAI Corpus Builder for SLM Distillation")
    parser.add_argument("--input_dir", type=str, help="Directory containing raw EA docs")
    parser.add_argument("--output", type=str, default="backend/data/synthetic_corpus.jsonl", help="Output JSONL file")

    args = parser.parse_args()

    if args.input_dir:
        builder = CorpusBuilder(output_file=args.output)
        asyncio.run(builder.process_directory(args.input_dir))
    else:
        print("Please provide an --input_dir")
