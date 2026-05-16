from typing import TypedDict, Annotated
from operator import add

class AgentState(TypedDict):
    objective: str
    context: Annotated[str, add]
    plan: str
    design: dict
    feedback: str
    final_hld: dict
    messages: Annotated[list, add]

# Full LangGraph workflow will be in graph/workflow.py
