import os
import sys
import json
import asyncio
import logging
import argparse
import random
import time
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

from dotenv import load_dotenv

# Load environment variables from .env if it exists
load_dotenv()
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

# Import get_llm from backend app
try:
    from app.agents.base_agent import get_llm
except ImportError as e:
    logger.error(f"Failed to import backend dependencies: {e}")
    sys.exit(1)

class EACorpusGenerator:
    """
    Uses the master index + processed docs + guidance files to generate high-quality
    training data for SLM distillation in ShareGPT format.
    """
    def __init__(self, output_file: str, model: str = None, batch_size: int = 5):
        self.output_file = output_file
        self.batch_size = batch_size
        self.model = model
        self.lock = asyncio.Lock()
        try:
            self.llm = get_llm(temperature=0.8, model=self.model)
            logger.info(f"Initialized LLM with model: {self.model or 'default'}")
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

        # Enhanced skill instruction
        if skill:
            skill_instruction = f"The dialogue MUST specifically showcase the ArchAI skill: {skill}."
        else:
            skill_instruction = """The dialogue must demonstrate proper use of multiple ArchAI skills:
            - ARCHAI:think-before-architecting: Analyze the problem deeply before proposing solutions.
            - ARCHAI:tradeoff-matrix: Explicitly compare options using a matrix (cost, complexity, performance, etc.).
            - ARCHAI:reuse-first: Evaluate existing enterprise assets before building new ones."""

        prompt = f"""
        You are the ArchAI Synthetic Data Engine, a high-fidelity teacher model.
        Your goal is to generate {num_examples} extremely high-quality, professional, and diverse architectural dialogues.

        --- ARCHAI PHILOSOPHY & GUARDRAILS (MANDATORY) ---
        {guidance}

        --- TASK ---
        Generate {num_examples} dialogue(s) in ShareGPT format between a 'human' and 'gpt' (ArchAI).

        --- TECHNICAL CONTEXT ({source_name}) ---
        {context_content[:10000]}

        --- QUALITY REQUIREMENTS ---
        1. ASSISTANT IDENTITY: ArchAI is a surgical, evidence-based Enterprise Architect. Never be generic. Always cite patterns or principles from the context.
        2. SKILLS: {skill_instruction}
        3. COMPLEXITY: The 'human' represents a CTO or Lead Architect. Questions should be hard, involving legacy constraints, budget, and scale.
        4. MULTI-TURN: {turns_instruction} Turns 2 and 3 should push back on the assistant's initial recommendation to force deeper reasoning.
        5. GUARDRAILS: Strictly follow all ARCHAI-GUARDRAILS. No fluff. No excessive pleasantries.
        6. OUTPUT FORMAT: Output ONLY a JSON list of objects. Each object must have a "conversations" key.

        Example Format:
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

        Output ONLY valid raw JSON.
        """

        max_retries = 8
        for attempt in range(max_retries):
            try:
                response = await self.llm.ainvoke(prompt)
                # Clean the response content
                clean_content = response.content.strip()
                if clean_content.startswith("```json"):
                    clean_content = clean_content[7:-3].strip()
                elif clean_content.startswith("```"):
                    clean_content = clean_content[3:-3].strip()

                # Basic validation that it's JSON
                data = json.loads(clean_content)
                if not isinstance(data, list):
                    data = [data]

                os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
                async with self.lock:
                    with open(self.output_file, "a", encoding="utf-8") as f:
                        for entry in data:
                            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                logger.info(f"Appended {len(data)} examples from {source_name} to {self.output_file}")
                return # Success
            except Exception as e:
                # Detect rate limit errors and apply heavier backoff
                error_str = str(e).lower()
                if "rate_limit" in error_str or "429" in error_str:
                    wait_time = (5 ** (attempt + 1)) + random.uniform(5, 15)
                    logger.warning(f"Rate limit hit for {source_name}. Backing off for {wait_time:.2f}s...")
                else:
                    wait_time = (2 ** attempt) + random.uniform(1, 5)
                    logger.warning(f"Attempt {attempt+1} failed for {source_name}: {e}. Retrying in {wait_time:.2f}s...")

                await asyncio.sleep(wait_time)

        logger.error(f"Failed to generate after {max_retries} attempts for {source_name}")

async def main():
    parser = argparse.ArgumentParser(description="ArchAI EA Corpus Generator for SLM Distillation")
    parser.add_argument("--master_sources", type=str, default="backend/data/master_sources.json")
    parser.add_argument("--processed_docs", type=str, default="backend/data/processed_docs.json")
    parser.add_argument("--output", type=str, default="backend/data/synthetic_corpus.jsonl")
    parser.add_argument("--total_count", type=int, default=10, help="Total target number of examples")
    parser.add_argument("--max_sources", type=int, default=100, help="Limit total sources processed for balancing")
    parser.add_argument("--skill", type=str, default=None, help="Focus generation on a specific ArchAI skill")
    parser.add_argument("--model", type=str, default=os.getenv("TEACHER_MODEL"), help="Teacher model name")
    parser.add_argument("--append", action="store_true")

    args = parser.parse_args()

    generator = EACorpusGenerator(args.output, model=args.model)

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

    # Determine how many examples per prompt
    EXAMPLES_PER_PROMPT = 2

    # We want total_count, so we need total_count // EXAMPLES_PER_PROMPT calls
    needed_calls = (args.total_count + EXAMPLES_PER_PROMPT - 1) // EXAMPLES_PER_PROMPT

    # Repeat or sample enough work items
    final_work_plan = []
    while len(final_work_plan) < needed_calls:
        random.shuffle(all_work)
        final_work_plan.extend(all_work[:needed_calls - len(final_work_plan)])

    logger.info(f"Generated a plan for {len(final_work_plan)} LLM calls to hit target ~{args.total_count} examples.")

    # Process in batches to avoid overwhelming LLM or rate limits
    batch_size = 2 # Small batch for Groq rate limits
    for i in range(0, len(final_work_plan), batch_size):
        batch = final_work_plan[i:i+batch_size]
        tasks = [generator.generate_examples(content, name, EXAMPLES_PER_PROMPT, skill=args.skill) for content, name in batch]
        await asyncio.gather(*tasks)
        logger.info(f"Processed batch {i//batch_size + 1}/{(len(final_work_plan)-1)//batch_size + 1}")
        await asyncio.sleep(2) # Respectful delay between batches

if __name__ == "__main__":
    asyncio.run(main())
