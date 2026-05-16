from langgraph.graph import StateGraph, END
from app.agents.base_agent import get_llm
from app.agents.orchestrator import AgentState
from app.models.artifacts import HLDDocument

llm = get_llm()

def orchestrator_node(state: AgentState):
    prompt = f"Lead Architect: Objective {state['objective']}. Context: {state.get('context','')}. Create Plan."
    response = llm.invoke(prompt)
    return {"plan": response.content, "messages": [response]}

def knowledge_node(state: AgentState):
    # Mock knowledge retrieval
    return {"context": "Existing System: CRM_PROD. License: Enterprise.", "messages": ["Retrieved CRM data."]}

def design_node(state: AgentState):
    # Mock design generation
    design = {
        "title": "New Integration",
        "high_level_design": "Connect CRM to Analytics via Event Hub.",
        "diagrams": [{"view": "logical", "mermaid_code": "graph LR; CRM-->EH; EH-->Analytics;", "description": "Flow"}]
    }
    return {"design": design, "messages": ["Generated Design."]}

def reviewer_node(state: AgentState):
    # Mock review
    return {"feedback": "Looks solid. High confidence.", "messages": ["Review complete."]}

def finalize_node(state: AgentState):
    # Map design to HLDDocument
    hld = HLDDocument(
        title=state['design']['title'],
        objective=state['objective'],
        high_level_design=state['design']['high_level_design'],
        diagrams=state['design']['diagrams'],
        decision_matrix=[],
        risks_and_mitigations=[],
        compliance_summary="Fully compliant.",
        confidence_score=95.0
    )
    return {"final_hld": hld.dict()}

# Build Workflow
workflow = StateGraph(AgentState)
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("knowledge_retrieval", knowledge_node)
workflow.add_node("design", design_node)
workflow.add_node("review", reviewer_node)
workflow.add_node("finalize", finalize_node)

workflow.set_entry_point("orchestrator")
workflow.add_edge("orchestrator", "knowledge_retrieval")
workflow.add_edge("knowledge_retrieval", "design")
workflow.add_edge("design", "review")
workflow.add_edge("review", "finalize")
workflow.add_edge("finalize", END)

graph = workflow.compile()
