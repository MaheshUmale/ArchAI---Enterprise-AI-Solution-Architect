from langgraph.graph import StateGraph, END
from app.agents.base_agent import get_llm
from app.agents.orchestrator import AgentState
from app.models.artifacts import HLDDocument

llm = get_llm()

def orchestrator_node(state: AgentState):
    # Main reasoning logic
    prompt = f"""You are the lead Solution Architect.
    Objective: {state['objective']}
    Available context: {state.get('context', '')}

    Create a detailed plan for design generation."""
    response = llm.invoke(prompt)
    return {"plan": response.content}

# Build the graph
workflow = StateGraph(AgentState)
workflow.add_node("orchestrator", orchestrator_node)
workflow.set_entry_point("orchestrator")
workflow.add_edge("orchestrator", END)

# Compile
graph = workflow.compile()
