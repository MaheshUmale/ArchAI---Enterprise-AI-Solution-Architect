from typing import List
from app.models.artifacts import HLDDocument

class ArtifactGenerator:
    @staticmethod
    def to_markdown(hld: HLDDocument) -> str:
        md = f"# {hld.title}\n\n"
        md += f"## Objective\n{hld.objective}\n\n"
        md += f"## Design\n{hld.high_level_design}\n\n"

        for diag in hld.diagrams:
            md += f"### {diag.view} View\n"
            md += f"```mermaid\n{diag.mermaid_code}\n```\n"
            md += f"{diag.description}\n\n"

        return md

    @staticmethod
    def generate_pdf(markdown_content: str, output_path: str):
        # Implementation would use a library like reportlab or md2pdf
        pass
