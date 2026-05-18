import os
import re
import json
import logging
import argparse
from typing import List, Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MasterSourceParser:
    """
    Parses MASTER-EA-SOURCES.md and prepares data for ingestion into Neo4j and vector stores.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.sources = []

    def parse(self) -> List[Dict]:
        if not os.path.exists(self.filepath):
            logger.error(f"Source file not found: {self.filepath}")
            return []

        logger.info(f"Parsing master sources from {self.filepath}...")
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read file {self.filepath}: {e}")
            return []

        # Split by level 2 headers (Sections)
        sections = re.split(r'\n## ', content)
        for section in sections[1:]:
            lines = section.split('\n')
            section_name = lines[0].strip()
            logger.debug(f"Processing section: {section_name}")

            # Find items like: 1. **[Title](URL)**
            current_source = None

            for line in lines[1:]:
                # Match the numbered list item with title and URL
                item_match = re.match(r'^\d+\.\s+\*\*\[(.*?)\]\((.*?)\)\*\*', line.strip())
                if item_match:
                    if current_source:
                        self.sources.append(current_source)

                    current_source = {
                        "title": item_match.group(1),
                        "url": item_match.group(2),
                        "authority": "Various",
                        "topic": section_name,
                        "description": "No description available.",
                        "source_type": "official_master_index"
                    }
                    continue

                # Extract metadata from the bullet points following the title
                if current_source:
                    # Match Authority
                    auth_match = re.match(r'^\s+-\s+\*Authority\*:\s*(.*)', line)
                    if auth_match:
                        current_source["authority"] = auth_match.group(1).strip()
                        continue

                    # Match Topic
                    topic_match = re.match(r'^\s+-\s+\*Topic\*:\s*(.*)', line)
                    if topic_match:
                        current_source["topic"] = topic_match.group(1).strip()
                        continue

                    # Match Description
                    desc_match = re.match(r'^\s+-\s+\*Description\*:\s*(.*)', line)
                    if desc_match:
                        current_source["description"] = desc_match.group(1).strip()
                        continue

            # Append the last source in the section
            if current_source:
                self.sources.append(current_source)

        logger.info(f"Successfully parsed {len(self.sources)} sources.")
        return self.sources

    def save_json(self, output_path: str):
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self.sources, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved parsed sources to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save JSON to {output_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="ArchAI Master EA Sources Ingestion Parser")
    parser.add_argument(
        "--input",
        type=str,
        default="docs/references/MASTER-EA-SOURCES.md",
        help="Path to the master sources markdown file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="backend/data/master_sources.json",
        help="Path to save the generated JSON"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    parser_instance = MasterSourceParser(args.input)
    sources = parser_instance.parse()

    if sources:
        parser_instance.save_json(args.output)
        logger.info("Ingestion preparation complete.")
    else:
        logger.warning("No sources were parsed. Check the input file format.")

if __name__ == "__main__":
    main()
