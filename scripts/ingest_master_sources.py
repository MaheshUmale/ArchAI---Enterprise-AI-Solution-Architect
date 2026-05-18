import os
import re
import json
import logging
import argparse
from typing import List, Dict, Any
import pdfplumber
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MasterSourceParser:
    """
    Parses MASTER-EA-SOURCES.md and prepares data for ingestion.
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

        logger.info(f"Successfully parsed {len(self.sources)} sources from index.")
        return self.sources

class DocumentProcessor:
    """
    Processes PDF and EPUB files from a directory.
    """
    def __init__(self, directory: str, max_pages: int = 20):
        self.directory = directory
        self.processed_docs = []
        self.max_pages = max_pages

    def clean_text(self, text: str) -> str:
        # Remove multiple newlines and spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove non-printable characters
        text = "".join(filter(lambda x: x.isprintable() or x == '\n', text))
        return text.strip()

    def process_pdf(self, filepath: str) -> str:
        text = ""
        try:
            with pdfplumber.open(filepath) as pdf:
                pages_to_process = pdf.pages[:self.max_pages] if self.max_pages > 0 else pdf.pages
                for page in pages_to_process:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.error(f"Error processing PDF {filepath}: {e}")
        return self.clean_text(text)

    def process_epub(self, filepath: str) -> str:
        text = ""
        try:
            book = epub.read_epub(filepath)
            items = list(book.get_items())
            doc_items = [item for item in items if item.get_type() == ebooklib.ITEM_DOCUMENT]

            # Process a subset of items to save time/memory
            items_to_process = doc_items[:10] if self.max_pages > 0 else doc_items

            for item in items_to_process:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text += soup.get_text() + "\n"
        except Exception as e:
            logger.error(f"Error processing EPUB {filepath}: {e}")
        return self.clean_text(text)

    def process_directory(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.directory):
            logger.warning(f"Directory not found: {self.directory}")
            return []

        files = [f for f in os.listdir(self.directory) if f.lower().endswith(('.pdf', '.epub'))]
        logger.info(f"Processing {len(files)} documents from {self.directory} (Max pages/items limit: {self.max_pages})...")

        for filename in tqdm(files, desc="Processing Docs"):
            filepath = os.path.join(self.directory, filename)
            content = ""
            if filename.lower().endswith('.pdf'):
                content = self.process_pdf(filepath)
            elif filename.lower().endswith('.epub'):
                content = self.process_epub(filepath)

            if content:
                self.processed_docs.append({
                    "filename": filename,
                    "content": content,
                    "source_type": "local_document",
                    "file_type": "pdf" if filename.lower().endswith('.pdf') else "epub"
                })

        return self.processed_docs

def main():
    parser = argparse.ArgumentParser(description="ArchAI Master EA Sources Ingestion & Doc Processing")
    parser.add_argument(
        "--index",
        type=str,
        default="docs/references/MASTER-EA-SOURCES.md",
        help="Path to the master sources markdown file"
    )
    parser.add_argument(
        "--doc_dir",
        type=str,
        default="docs/EA_CLOUD_DESIGN PATTERNS/",
        help="Directory containing PDF/EPUB files"
    )
    parser.add_argument(
        "--output_index",
        type=str,
        default="backend/data/master_sources.json",
        help="Path to save the generated index JSON"
    )
    parser.add_argument(
        "--output_docs",
        type=str,
        default="backend/data/processed_docs.json",
        help="Path to save the processed documents JSON"
    )
    parser.add_argument(
        "--max_pages",
        type=int,
        default=20,
        help="Max pages per PDF or items per EPUB to process (0 for unlimited)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # 1. Parse Index
    index_parser = MasterSourceParser(args.index)
    sources = index_parser.parse()
    if sources:
        os.makedirs(os.path.dirname(args.output_index), exist_ok=True)
        with open(args.output_index, "w", encoding="utf-8") as f:
            json.dump(sources, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved parsed sources to {args.output_index}")

    # 2. Process Local Documents
    doc_processor = DocumentProcessor(args.doc_dir, max_pages=args.max_pages)
    docs = doc_processor.process_directory()
    if docs:
        os.makedirs(os.path.dirname(args.output_docs), exist_ok=True)
        with open(args.output_docs, "w", encoding="utf-8") as f:
            json.dump(docs, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved processed documents to {args.output_docs}")

    logger.info("Ingestion and document processing complete.")

if __name__ == "__main__":
    main()
