import os
import re
import json
from typing import List, Dict

class MasterSourceParser:
    """
    Parses MASTER-EA-SOURCES.md and prepares data for ingestion.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.sources = []

    def parse(self):
        if not os.path.exists(self.filepath):
            print(f"Error: {self.filepath} not found.")
            return []

        with open(self.filepath, "r") as f:
            content = f.read()

        # Split by sections
        sections = re.split(r'\n## ', content)
        for section in sections[1:]:
            lines = section.split('\n')
            section_name = lines[0].strip()

            # Find items like: 1. **[Title](URL)**
            # We use a line-by-line approach to be more robust with multi-line metadata
            current_source = None

            for line in lines[1:]:
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

                if current_source:
                    auth_match = re.match(r'^\s+-\s+\*Authority\*:\s*(.*)', line)
                    if auth_match:
                        current_source["authority"] = auth_match.group(1).strip()
                        continue

                    topic_match = re.match(r'^\s+-\s+\*Topic\*:\s*(.*)', line)
                    if topic_match:
                        current_source["topic"] = topic_match.group(1).strip()
                        continue

                    desc_match = re.match(r'^\s+-\s+\*Description\*:\s*(.*)', line)
                    if desc_match:
                        current_source["description"] = desc_match.group(1).strip()
                        continue

            if current_source:
                self.sources.append(current_source)

        return self.sources

    def save_json(self, output_path: str):
        with open(output_path, "w") as f:
            json.dump(self.sources, f, indent=2)
        print(f"Saved {len(self.sources)} sources to {output_path}")

if __name__ == "__main__":
    parser = MasterSourceParser("docs/references/MASTER-EA-SOURCES.md")
    sources = parser.parse()
    os.makedirs("backend/data", exist_ok=True)
    parser.save_json("backend/data/master_sources.json")
    print("Ingestion preparation complete.")
