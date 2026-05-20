import os
import re
import json
import asyncio
import logging
import subprocess
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import httpx
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DesignPatternIngestor:
    def __init__(self, input_md="Architectural Design Patterns.md", output_dir="docs/design_patterns"):
        self.input_md = input_md
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.priority_sections = [
            'General Architecture',
            'Cloud Architecture',
            'Serverless Architecture',
            'Micro services & Distributed Systems',
            'Enterprise Integration Patterns',
            'Databases and Storage',
            'Security',
            'Books'
        ]

    def extract_sources(self):
        with open(self.input_md, 'r', encoding='utf-8') as f:
            content = f.read()

        sections = re.findall(r'## (.*?)\n(.*?)(?=\n##|$)', content, re.DOTALL)
        sources = []
        for section_name, section_content in sections:
            if any(ps.lower() in section_name.lower() for ps in self.priority_sections):
                links = re.findall(r'- \[(.*?)\]\((.*?)\)', section_content)
                for title, url in links:
                    authority = urlparse(url).netloc
                    sources.append({
                        "title": title.strip(),
                        "url": url.strip(),
                        "topic": section_name.strip(),
                        "authority": authority,
                        "description": f"Source for {title.strip()} patterns."
                    })
        return sources

    async def fetch_url(self, client, url):
        try:
            response = await client.get(url, timeout=20.0, follow_redirects=True)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
        return None

    def clean_html(self, html, title):
        if not html: return ""
        soup = BeautifulSoup(html, 'html.parser')

        # Remove scripts, styles, nav, footer
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Try to find main content
        main = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article'))
        if main:
            text = main.get_text(separator='\n')
        else:
            text = soup.get_text(separator='\n')

        # Basic cleaning
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return f"# {title}\n\n{text.strip()}"

    async def process_source(self, client, source):
        safe_title = "".join([c if c.isalnum() else "_" for c in source["title"]])
        output_file = os.path.join(self.output_dir, f"{safe_title}.md")

        if os.path.exists(output_file):
            return output_file

        url = source["url"]
        parsed_url = urlparse(url)

        if url.endswith(".pdf"):
            # Use curl for PDF
            try:
                pdf_path = os.path.join(self.output_dir, f"{safe_title}.pdf")
                subprocess.run(["curl", "-L", "-s", "-o", pdf_path, url], timeout=30)
                return pdf_path
            except:
                return None

        if parsed_url.netloc == "github.com":
            # Maybe just fetch README for now if it's a repo
            if "/tree/" not in parsed_url.path and "/blob/" not in parsed_url.path:
                # Append readme path if it's a root repo url
                raw_url = url.replace("github.com", "raw.githubusercontent.com") + "/master/README.md"
                content = await self.fetch_url(client, raw_url)
                if not content:
                    raw_url = url.replace("github.com", "raw.githubusercontent.com") + "/main/README.md"
                    content = await self.fetch_url(client, raw_url)

                if content:
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    return output_file

        # Default HTML to MD conversion
        html = await self.fetch_url(client, url)
        if html:
            md_content = self.clean_html(html, source["title"])
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(md_content)
            return output_file

        return None

    async def run(self):
        sources = self.extract_sources()
        logger.info(f"Found {len(sources)} sources to process.")

        async with httpx.AsyncClient() as client:
            tasks = [self.process_source(client, src) for src in sources]
            results = []
            for task in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Downloading sources"):
                results.append(await task)

        logger.info(f"Successfully processed {len([r for r in results if r])} sources.")
        return sources

if __name__ == "__main__":
    ingestor = DesignPatternIngestor()
    asyncio.run(ingestor.run())
