from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TradeOffOption(BaseModel):
    option: str
    score: float
    reason: str

class DecisionMatrix(BaseModel):
    decision: str
    options: List[TradeOffOption]
    recommended: str
    justification: str

class ArchitectureDiagram(BaseModel):
    view: str  # logical, physical, data_flow, security
    mermaid_code: str
    description: str

class HLDDocument(BaseModel):
    title: str
    objective: str
    high_level_design: str
    diagrams: List[ArchitectureDiagram]
    decision_matrix: List[DecisionMatrix]
    risks_and_mitigations: List[Dict[str, Any]]
    compliance_summary: str
    confidence_score: float = Field(ge=0, le=100)

class DesignRequest(BaseModel):
    objective: str
    additional_context: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None
