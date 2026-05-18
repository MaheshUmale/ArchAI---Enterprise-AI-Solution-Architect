import json
import os
from typing import List, Dict
from app.agents.base_agent import get_llm
from app.core.config import settings

class CorpusBuilder:
    """
    Synthesizes high-quality EA training data from knowledge base assets.
    Implements the philosophy of smart curation for SLM distillation.
    """
    def __init__(self):
        self.llm = get_llm(temperature=0.7) # Higher temp for diverse synthesis
        self.output_path = "backend/data/synthetic_corpus.jsonl"

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
        """

        response = await self.llm.ainvoke(prompt)
        return {"content": response.content}

    def save_to_corpus(self, data: Dict):
        with open(self.output_path, "a") as f:
            f.write(json.dumps(data) + "\n")

# Example usage script would go here
