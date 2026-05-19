import os
import re
import json
import logging
import argparse
import hashlib
from typing import List, Dict, Any
import pdfplumber
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from tqdm import tqdm

try:
    from unstructured.partition.pdf import partition_pdf
    HAS_UNSTRUCTURED = True
except ImportError:
    HAS_UNSTRUCTURED = False

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
    Processes PDF and EPUB files with advanced cleaning, chunking, and deduplication.
    """
    def __init__(self, directory: str, max_pages: int = 50, chunk_size: int = 4000, chunk_overlap: int = 400, use_unstructured: bool = True):
        self.directory = directory
        self.processed_docs = []
        self.max_pages = max_pages
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.seen_hashes = set()
        self.use_unstructured = use_unstructured and HAS_UNSTRUCTURED

    def clean_text(self, text: str) -> str:
        # 1. Remove common headers/footers patterns (e.g., "Page X of Y", lone numbers at start/end of lines)
        text = re.sub(r'(?m)^\s*\d+\s*$', '', text) # Lone numbers
        text = re.sub(r'(?i)Page \d+ of \d+', '', text)
        text = re.sub(r'(?i)Copyright ©.*', '', text)

        # 2. Remove multiple newlines and spaces
        text = re.sub(r'\s+', ' ', text)

        # 3. Remove non-printable characters
        text = "".join(filter(lambda x: x.isprintable() or x == '\n', text))

        return text.strip()

    def chunk_text(self, text: str) -> List[str]:
        """Sliding window chunking."""
        if not text:
            return []

        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size

            # Try to snap to nearest space to avoid cutting words
            if end < len(text):
                actual_end = text.rfind(' ', start, end)
                if actual_end > start + (self.chunk_size * 0.7):
                    end = actual_end

            chunk = text[start:end]

            # Deduplication at chunk level
            chunk_hash = hashlib.md5(chunk.encode()).hexdigest()
            if chunk_hash not in self.seen_hashes:
                chunks.append(chunk.strip())
                self.seen_hashes.add(chunk_hash)

            # Correctly advance start pointer based on actual end and overlap
            start = end - self.chunk_overlap
            if start < 0: start = end # Prevent infinite loops if overlap is too large
            if start >= len(text): break

        return chunks

    def process_pdf(self, filepath: str) -> Dict[str, Any]:
        text = ""
        metadata = {}

        if self.use_unstructured:
            logger.info(f"Using Unstructured for {filepath}")
            try:
                # Use strategy='fast' or 'hi_res' depending on needs. fast is usually enough for digital PDFs.
                elements = partition_pdf(filename=filepath, strategy="fast")
                text = "\n".join([str(el) for el in elements])
            except Exception as e:
                logger.warning(f"Unstructured failed for {filepath}: {e}. Falling back to pdfplumber.")
                text = self._process_pdf_plumber(filepath)
        else:
            text = self._process_pdf_plumber(filepath)

        # Attempt to get metadata via pdfplumber regardless of extraction method
        try:
            with pdfplumber.open(filepath) as pdf:
                metadata = pdf.metadata
        except:
            pass

        cleaned_text = self.clean_text(text)
        chunks = self.chunk_text(cleaned_text)

        return {
            "title": metadata.get('Title', os.path.basename(filepath)),
            "author": metadata.get('Author', 'Unknown'),
            "chunks": chunks
        }

    def _process_pdf_plumber(self, filepath: str) -> str:
        text = ""
        try:
            with pdfplumber.open(filepath) as pdf:
                pages_to_process = pdf.pages[:self.max_pages] if self.max_pages > 0 else pdf.pages
                for page in pages_to_process:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.error(f"Error processing PDF with pdfplumber {filepath}: {e}")
        return text

    def process_epub(self, filepath: str) -> Dict[str, Any]:
        text = ""
        title = os.path.basename(filepath)
        author = "Unknown"
        try:
            book = epub.read_epub(filepath)
            title_meta = book.get_metadata('DC', 'title')
            if title_meta: title = title_meta[0][0]

            author_meta = book.get_metadata('DC', 'creator')
            if author_meta: author = author_meta[0][0]

            items = list(book.get_items())
            doc_items = [item for item in items if item.get_type() == ebooklib.ITEM_DOCUMENT]

            items_to_process = doc_items[:15] if self.max_pages > 0 else doc_items

            for item in items_to_process:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                for tag in soup(["script", "style"]):
                    tag.decompose()
                text += soup.get_text() + "\n"
        except Exception as e:
            logger.error(f"Error processing EPUB {filepath}: {e}")

        cleaned_text = self.clean_text(text)
        chunks = self.chunk_text(cleaned_text)

        return {
            "title": title,
            "author": author,
            "chunks": chunks
        }

    def process_directory(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.directory):
            logger.warning(f"Directory not found: {self.directory}")
            return []

        files = [f for f in os.listdir(self.directory) if f.lower().endswith(('.pdf', '.epub'))]
        logger.info(f"Processing {len(files)} docs from {self.directory} (Chunking enabled, Use Unstructured: {self.use_unstructured})...")

        for filename in tqdm(files, desc="Processing Docs"):
            filepath = os.path.join(self.directory, filename)
            result = None
            if filename.lower().endswith('.pdf'):
                result = self.process_pdf(filepath)
            elif filename.lower().endswith('.epub'):
                result = self.process_epub(filepath)

            if result and result["chunks"]:
                self.processed_docs.append({
                    "filename": filename,
                    "title": result["title"],
                    "author": result["author"],
                    "chunks": result["chunks"],
                    "source_type": "local_document",
                    "file_type": "pdf" if filename.lower().endswith('.pdf') else "epub"
                })

        return self.processed_docs

def main():
    parser = argparse.ArgumentParser(description="ArchAI Master EA Sources Ingestion & Advanced Doc Processing")
    parser.add_argument("--index", type=str, default="docs/references/MASTER-EA-SOURCES.md")
    parser.add_argument("--doc_dir", type=str, default="docs/EA_CLOUD_DESIGN PATTERNS/")
    parser.add_argument("--output_index", type=str, default="backend/data/master_sources.json")
    parser.add_argument("--output_docs", type=str, default="backend/data/processed_docs.json")
    parser.add_argument("--max_pages", type=int, default=50)
    parser.add_argument("--chunk_size", type=int, default=4000)
    parser.add_argument("--overlap", type=int, default=400)
    parser.add_argument("--no_unstructured", action="store_true", help="Disable Unstructured PDF processing")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # 1. Parse Index
    try:
        index_parser = MasterSourceParser(args.index)
        sources = index_parser.parse()
        if sources:
            os.makedirs(os.path.dirname(args.output_index), exist_ok=True)
            with open(args.output_index, "w", encoding="utf-8") as f:
                json.dump(sources, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved parsed sources to {args.output_index}")
    except Exception as e:
        logger.error(f"Failed to parse index: {e}")

    # 2. Process Local Documents with Chunking
    try:
        doc_processor = DocumentProcessor(
            args.doc_dir,
            max_pages=args.max_pages,
            chunk_size=args.chunk_size,
            chunk_overlap=args.overlap,
            use_unstructured=not args.no_unstructured
        )
        docs = doc_processor.process_directory()
        if docs:
            os.makedirs(os.path.dirname(args.output_docs), exist_ok=True)
            with open(args.output_docs, "w", encoding="utf-8") as f:
                json.dump(docs, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved processed documents to {args.output_docs}")
    except Exception as e:
        logger.error(f"Failed to process documents: {e}")

    logger.info("Ingestion and advanced document processing complete.")

if __name__ == "__main__":
    main()
