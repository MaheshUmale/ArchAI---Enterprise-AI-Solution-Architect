from app.agents.base_agent import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.models.artifacts import HLDDocument
from app.agents.skills import ArchAISkills
from typing import Dict
import os

def load_base_prompt():
    # Use absolute path relative to project root (ArchAI root)
    # Assumes execution from root as per instructions
    path = os.path.join(os.getcwd(), "docs/prompts/BASE_AGENT_PROMPT.md")
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    return "You are an expert Solution Architect."

class DesignAgent:
    def __init__(self):
        self.llm = get_llm()
        self.parser = JsonOutputParser(pydantic_object=HLDDocument)
        self.base_prompt = load_base_prompt()
        self.skills = ArchAISkills()

    def generate(self, objective: str, context: str) -> HLDDocument:
        system_prompt = f"{self.base_prompt}\n\nRole Specific: You are the Design Agent. Generate structured HLD with technical descriptions. Do not worry about diagram syntax; a specialized agent will handle that."
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "Objective: {objective}\n\nContext: {context}")
        ])

        chain = prompt | self.llm | self.parser
        return chain.invoke({"objective": objective, "context": context})

class DiagramAgent:
    def __init__(self):
        self.llm = get_llm(temperature=0.0)

    def generate_diagram(self, design_text: str) -> str:
        prompt = f"""
        You are a Mermaid JS and C4 Model Expert.
        Based on the following design description, generate a valid Mermaid graph (Flowchart or C4Context).

        DESIGN:
        {design_text}

        Output ONLY the Mermaid code. Ensure syntax is 100% correct.
        """
        response = self.llm.invoke(prompt)
        return response.content.strip()

    def self_correct(self, diagram_code: str, error_message: str) -> str:
        prompt = f"""
        The following Mermaid code has a syntax error. Fix it.

        CODE:
        {diagram_code}

        ERROR:
        {error_message}

        Output ONLY the fixed Mermaid code.
        """
        response = self.llm.invoke(prompt)
        return response.content.strip()

class ReviewAgent:
    def __init__(self):
        self.llm = get_llm()
        self.base_prompt = load_base_prompt()

    def review(self, hld: HLDDocument) -> Dict:
        system_prompt = f"{self.base_prompt}\n\nRole Specific: You are the Reviewer Agent. Critique the design for security, cost, and compliance."
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "HLD: {hld_json}")
        ])

        response = self.llm.invoke(prompt.format(hld_json=hld.model_dump_json()))
        return {"feedback": response.content, "score": 90.0}

class ReuseComplianceAgent:
    def __init__(self):
        self.llm = get_llm()
        self.base_prompt = load_base_prompt()

    def check(self, design: Dict) -> Dict:
        system_prompt = f"{self.base_prompt}\n\nRole Specific: You are the Reuse & Compliance Agent. Enforce reuse-before-buy and verify policy alignment."
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "Design to check: {design}")
        ])
        response = self.llm.invoke(prompt.format(design=design))
        return {"compliance_report": response.content}

class TradeoffCostAgent:
    def __init__(self):
        self.llm = get_llm()
        self.base_prompt = load_base_prompt()

    def analyze(self, design: Dict) -> Dict:
        system_prompt = f"{self.base_prompt}\n\nRole Specific: You are the Trade-off & Cost Agent. Provide a scored matrix (Cost, Performance, Security, etc.)"
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "Design to analyze: {design}")
        ])
        response = self.llm.invoke(prompt.format(design=design))
        return {"tradeoff_analysis": response.content}
