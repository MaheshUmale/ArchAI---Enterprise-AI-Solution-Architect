from app.agents.base_agent import get_llm
from app.knowledge.vector_service import vector_service

class KnowledgeAgent:
    def __init__(self):
        self.llm = get_llm()

    def run(self, state):
        # Retrieval logic
        objective = state['objective']
        context = vector_service.query(objective)
        state['context'] += f"\nRetrieved Knowledge: {context}"
        return state
