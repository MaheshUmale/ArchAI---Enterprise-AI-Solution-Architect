from fastapi import APIRouter
from app.models.artifacts import DesignRequest, HLDDocument
from app.graph.workflow import graph

router = APIRouter()

@router.post("/design", response_model=HLDDocument)
async def generate_design(request: DesignRequest):
    initial_state = {
        "objective": request.objective,
        "context": request.additional_context or "",
        "messages": []
    }

    result = graph.invoke(initial_state)
    return result.get("final_hld")
