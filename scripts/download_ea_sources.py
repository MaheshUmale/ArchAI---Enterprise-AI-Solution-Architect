import json
import os
import subprocess
import time
from typing import List, Dict

class EACourseDownloader:
    """
    Downloads EA authoritative sources for local reference.
    """
    def __init__(self, sources_json: str, output_dir: str):
        self.sources_json = sources_json
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def load_sources(self) -> List[Dict]:
        with open(self.sources_json, "r") as f:
            return json.load(f)

    def download_source(self, source: Dict):
        url = source["url"]
        # Create a safe filename
        safe_title = "".join([c if c.isalnum() else "_" for c in source["title"]])
        filename = f"{safe_title}.html"
        filepath = os.path.join(self.output_dir, filename)

        if os.path.exists(filepath):
            print(f"Skipping {filename}, already exists.")
            return

        print(f"Downloading {source['title']} from {url}...")
        try:
            # Use curl for downloading
            result = subprocess.run(
                ["curl", "-L", "-s", "-o", filepath, url],
                timeout=30,
                capture_output=True
            )
            if result.returncode == 0:
                print(f"Successfully downloaded {filename}")
            else:
                print(f"Failed to download {filename}: {result.stderr.decode()}")
        except Exception as e:
            print(f"Error downloading {filename}: {e}")

    def run(self, limit: int = None):
        sources = self.load_sources()
        if limit:
            sources = sources[:limit]

        for source in sources:
            self.download_source(source)
            time.sleep(1)  # Respectful rate limiting

if __name__ == "__main__":
    downloader = EACourseDownloader(
        sources_json="backend/data/master_sources.json",
        output_dir="knowledge_base/external_references"
    )
    # Start with a small limit or full run
    downloader.run()
    print("Download process completed.")
