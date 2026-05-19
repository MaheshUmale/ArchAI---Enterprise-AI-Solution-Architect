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
    def __init__(self, output_file: str, batch_size: int = 5):
        self.output_file = output_file
        self.batch_size = batch_size
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

    async def generate_examples(self, context_content: str, source_name: str, num_examples: int = 1, multi_turn: bool = True, skill: str = None):
        guidance = self.load_guidance()

        turns_instruction = "Generate a multi-turn (3-4 turns) architectural dialogue." if multi_turn else "Generate a single-turn architectural dialogue."
        skill_instruction = f"The dialogue MUST specifically showcase the ArchAI skill: {skill}." if skill else "The dialogue must demonstrate proper use of ArchAI skills (think-before-architecting, tradeoff-matrix, reuse-first)."

        prompt = f"""
        You are the ArchAI Synthetic Data Engine.
        Your task is to generate {num_examples} extremely high-quality, multi-turn architectural dialogues between a Human and ArchAI (the GPT assistant).

        The dialogues must be in ShareGPT format.

        --- REQUIREMENTS ---
        1. ASSISTANT ROLE: ArchAI is an expert Enterprise Architect. It must be professional, evidence-based, and surgical.
        2. SKILLS: {skill_instruction}
        3. SOURCE GROUNDING: Base the technical advice on the provided context: {source_name}.
        4. COMPLEXITY: Human should ask complex, multi-layered enterprise questions (e.g., legacy migration, global scale, data mesh).
        5. MULTI-TURN: {turns_instruction} The Human should ask follow-up questions challenging the previous answer or asking for more detail.
        6. FORMAT: Output ONLY a JSON list of objects. Each object has a "conversations" key.

        --- ARCHAI GUIDANCE & SKILLS ---
        {guidance}

        --- CONTEXT CONTENT ({source_name}) ---
        {context_content[:8000]}

        Output ONLY valid JSON.
        """

        try:
            response = await self.llm.ainvoke(prompt)
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
            logger.error(f"Failed to generate or parse response from {source_name}: {e}")

async def main():
    parser = argparse.ArgumentParser(description="ArchAI EA Corpus Generator for SLM Distillation")
    parser.add_argument("--master_sources", type=str, default="backend/data/master_sources.json")
    parser.add_argument("--processed_docs", type=str, default="backend/data/processed_docs.json")
    parser.add_argument("--output", type=str, default="backend/data/synthetic_corpus.jsonl")
    parser.add_argument("--total_count", type=int, default=10, help="Total target number of examples")
    parser.add_argument("--max_sources", type=int, default=50, help="Limit total sources processed for balancing")
    parser.add_argument("--skill", type=str, default=None, help="Focus generation on a specific ArchAI skill")
    parser.add_argument("--append", action="store_true")

    args = parser.parse_args()

    generator = EACorpusGenerator(args.output)

    if not args.append and os.path.exists(args.output):
        logger.info(f"Overwriting existing output file: {args.output}")
        os.remove(args.output)

    all_work = []

    # Balanced Sampling: Master Index
    if os.path.exists(args.master_sources):
        with open(args.master_sources, "r", encoding="utf-8") as f:
            sources = json.load(f)
            by_topic = {}
            for s in sources:
                topic = s.get('topic', 'General')
                if topic not in by_topic: by_topic[topic] = []
                by_topic[topic].append(s)

            topics = list(by_topic.keys())
            random.shuffle(topics)
            processed_count = 0

            while processed_count < args.max_sources // 2 and topics:
                for topic in topics:
                    if not by_topic[topic]: continue
                    src = by_topic[topic].pop(random.randint(0, len(by_topic[topic]) - 1))
                    content = f"Title: {src['title']}\nTopic: {src['topic']}\nDescription: {src['description']}"
                    all_work.append((content, src['title']))
                    processed_count += 1
                    if processed_count >= args.max_sources // 2: break
                topics = [t for t in topics if by_topic[t]]

    # Balanced Sampling: Large Docs (Chunks)
    if os.path.exists(args.processed_docs):
        with open(args.processed_docs, "r", encoding="utf-8") as f:
            docs = json.load(f)
            random.shuffle(docs)
            processed_count = 0

            for doc in docs:
                if processed_count >= args.max_sources // 2: break
                chunks = doc.get('chunks', [])
                if not chunks: continue
                chunk = random.choice(chunks)
                all_work.append((chunk, doc['title']))
                processed_count += 1

    if not all_work:
        logger.error("No sources or documents found to generate from.")
        return

    # Calculate examples per source to hit total_count
    examples_per_source = max(1, args.total_count // len(all_work))

    logger.info(f"Generated a plan for {len(all_work)} sources, ~{examples_per_source} examples each.")

    # Process in batches to avoid overwhelming LLM or rate limits
    batch_size = 5
    for i in range(0, len(all_work), batch_size):
        batch = all_work[i:i+batch_size]
        tasks = [generator.generate_examples(content, name, examples_per_source, skill=args.skill) for content, name in batch]
        await asyncio.gather(*tasks)
        logger.info(f"Processed batch {i//batch_size + 1}/{(len(all_work)-1)//batch_size + 1}")

if __name__ == "__main__":
    asyncio.run(main())
