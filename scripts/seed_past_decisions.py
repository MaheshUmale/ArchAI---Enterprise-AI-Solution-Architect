import os
import sys
import json
import asyncio
import argparse
import logging
import random
from typing import List, Dict

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

from dotenv import load_dotenv
load_dotenv()

try:
    from app.agents.base_agent import get_llm
except ImportError:
    print("Error: Missing backend dependencies.")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PastDecisionGenerator:
    def __init__(self, model: str = None):
        self.llm = get_llm(temperature=0.8, model=model)

    async def generate_decision(self, pattern: Dict) -> Dict:
        prompt = f"""
        You are a Principal Architect generating historical design records for an Enterprise Architecture repository.
        Based on the architectural pattern '{pattern['name']}', generate a realistic 'PastDecision' record.

        PATTERN DESCRIPTION: {pattern['description']}

        Output ONLY a JSON object with:
        {{
          "id": "dec-{random.randint(1000, 9999)}",
          "title": "A descriptive title for the decision",
          "context": "The technical and business environment that necessitated this decision.",
          "decision": "What specific choice was made (e.g., 'We chose Kafka over RabbitMQ for...').",
          "justification": "Detailed evidence-based reasoning, mentioning specific ArchAI skills like tradeoff-matrix or cost-benefit.",
          "tags": ["tag1", "tag2"]
        }}
        """

        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to generate decision for {pattern['name']}: {e}")
            return None

async def main():
    parser = argparse.ArgumentParser(description="Seed synthetic Past Decisions for ArchAI")
    parser.add_argument("--hld_kb", type=str, default="backend/data/hld_knowledge_base.json")
    parser.add_argument("--output", type=str, default="backend/data/past_decisions.json")
    parser.add_argument("--count", type=int, default=10)

    args = parser.parse_args()

    if not os.path.exists(args.hld_kb):
        logger.error(f"HLD Knowledge Base not found: {args.hld_kb}")
        return

    with open(args.hld_kb, "r") as f:
        kb = json.load(f)

    generator = PastDecisionGenerator()
    decisions = []

    patterns = kb.get("curated_patterns", [])
    if not patterns:
        logger.error("No patterns found in HLD KB.")
        return

    logger.info(f"Generating {args.count} synthetic past decisions...")
    for i in range(args.count):
        pattern = random.choice(patterns)
        decision = await generator.generate_decision(pattern)
        if decision:
            decisions.append(decision)
        logger.info(f"Generated {i+1}/{args.count}")
        await asyncio.sleep(1)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(decisions, f, indent=2)

    logger.info(f"Successfully seeded {len(decisions)} decisions to {args.output}")

if __name__ == "__main__":
    asyncio.run(main())
