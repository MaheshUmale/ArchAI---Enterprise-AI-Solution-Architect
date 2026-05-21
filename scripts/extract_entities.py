import os
import sys
import json
import asyncio
import logging
import argparse
from typing import List, Dict, Any

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

from dotenv import load_dotenv
load_dotenv()
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

try:
    from app.agents.base_agent import get_llm
except ImportError as e:
    print(f"Error: Missing dependencies. {e}")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EntityExtractor:
    def __init__(self, model: str = None):
        self.llm = get_llm(temperature=0.0, model=model)
        self.lock = asyncio.Lock()

    async def extract_from_chunk(self, chunk_text: str, source_title: str) -> Dict[str, Any]:
        prompt = f"""
        You are a Knowledge Graph Engineer for an Enterprise Architecture AI.
        Your goal is to extract structured entities and relationships from technical text.

        --- TEXT CHUNK ({source_title}) ---
        {chunk_text}

        --- SCHEMA ---
        Nodes:
        - System (id, name, type, cloud, status)
        - DataAsset (id, name, classification)
        - Owner (id, name, department)
        - License (id, name, cost, renewal_date)
        - Policy (id, name, description, severity)
        - PastDecision (id, title, context, decision, justification)

        Relationships:
        - (System)-[:FEEDS]->(System)
        - (System)-[:OWNED_BY]->(Owner)
        - (System)-[:HAS_LICENSE]->(License)
        - (System)-[:USES_DATA]->(DataAsset)
        - (System)-[:MUST_FOLLOW]->(Policy)

        --- TASK ---
        Extract as many relevant entities and relationships as possible from the text.
        Ensure IDs are unique and stable (e.g., lowercase-kebab-case).
        If a field like 'cloud' or 'status' is unknown, omit it.

        Output ONLY a JSON object with:
        {{
          "nodes": [ {{"label": "System", "properties": {{...}} }}, ... ],
          "relationships": [ {{"type": "FEEDS", "source_id": "...", "target_id": "...", "properties": {{...}} }}, ... ]
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
            logger.error(f"Extraction failed for chunk from {source_title}: {e}")
            return {"nodes": [], "relationships": []}

async def main():
    parser = argparse.ArgumentParser(description="Dynamic Ontology Mapping: Extract entities from docs")
    parser.add_argument("--input", type=str, default="backend/data/processed_docs.json")
    parser.add_argument("--output", type=str, default="backend/data/extracted_entities.json")
    parser.add_argument("--limit", type=int, default=10, help="Limit number of chunks to process for testing")
    parser.add_argument("--model", type=str, default=None)

    args = parser.parse_args()

    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return

    with open(args.input, "r", encoding="utf-8") as f:
        docs = json.load(f)

    extractor = EntityExtractor(model=args.model)
    all_extracted = {"nodes": [], "relationships": []}

    # Flatten docs into chunks for processing
    work_items = []
    for doc in docs:
        for chunk in doc.get("chunks", []):
            work_items.append((chunk, doc.get("title", "Unknown")))

    # Limit work items for safety/testing
    work_items = work_items[:args.limit]

    logger.info(f"Processing {len(work_items)} chunks for entity extraction...")

    # Process in batches
    batch_size = 3
    for i in range(0, len(work_items), batch_size):
        batch = work_items[i:i+batch_size]
        tasks = [extractor.extract_from_chunk(chunk, title) for chunk, title in batch]
        results = await asyncio.gather(*tasks)

        for res in results:
            all_extracted["nodes"].extend(res.get("nodes", []))
            all_extracted["relationships"].extend(res.get("relationships", []))

        logger.info(f"Processed batch {i//batch_size + 1}/{(len(work_items)-1)//batch_size + 1}")
        await asyncio.sleep(1)

    # Simple de-duplication based on node IDs
    unique_nodes = {}
    for node in all_extracted["nodes"]:
        node_id = node.get("properties", {}).get("id")
        if node_id:
            unique_nodes[node_id] = node

    all_extracted["nodes"] = list(unique_nodes.values())

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(all_extracted, f, indent=2)

    logger.info(f"Extracted {len(all_extracted['nodes'])} nodes and {len(all_extracted['relationships'])} relationships.")
    logger.info(f"Results saved to {args.output}")

if __name__ == "__main__":
    asyncio.run(main())
