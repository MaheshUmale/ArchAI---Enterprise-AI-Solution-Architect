from app.agents.base_agent import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.models.artifacts import HLDDocument
from typing import Dict

class DesignAgent:
    def __init__(self):
        self.llm = get_llm()
        self.parser = JsonOutputParser(pydantic_object=HLDDocument)

    def generate(self, objective: str, context: str) -> HLDDocument:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an Expert Solution Architect. Create a High-Level Design (HLD) in JSON format that follows the schema. "
                       "Include Mermaid diagrams for the architecture. Ensure the response is valid JSON."),
            ("user", "Objective: {objective}\n\nContext: {context}")
        ])

        chain = prompt | self.llm | self.parser
        return chain.invoke({"objective": objective, "context": context})

class ReviewAgent:
    def __init__(self):
        self.llm = get_llm()

    def review(self, hld: HLDDocument) -> Dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a Senior Reviewer and Compliance Officer. Review the following HLD for risks and compliance."),
            ("user", "HLD: {hld_json}")
        ])

        response = self.llm.invoke(prompt.format(hld_json=hld.model_dump_json()))
        # Simple review parsing for MVP
        return {"feedback": response.content, "score": 90.0}
