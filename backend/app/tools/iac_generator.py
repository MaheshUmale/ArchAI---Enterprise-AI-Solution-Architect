from app.agents.base_agent import get_llm
import logging

logger = logging.getLogger(__name__)

class IaCGenerator:
    """
    Translates Low-Level Designs into infrastructure-as-code skeletons.
    """
    def __init__(self):
        self.llm = get_llm(temperature=0.0)

    async def generate_terraform(self, lld_text: str) -> str:
        prompt = f"""
        You are a DevOps and Cloud Infrastructure Expert.
        Convert the following Low-Level Design (LLD) into a production-ready Terraform skeleton.
        Include providers, resources, and variables.

        LLD:
        {lld_text}

        Output ONLY the Terraform code block.
        """
        response = await self.llm.ainvoke(prompt)
        return response.content.strip()

iac_generator = IaCGenerator()
