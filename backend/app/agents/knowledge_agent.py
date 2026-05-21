from app.agents.base_agent import get_llm
from app.knowledge.vector_service import vector_service
from neo4j import GraphDatabase
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)

class KnowledgeAgent:
    def __init__(self):
        self.llm = get_llm(temperature=0.0)
        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
        except Exception as e:
            logger.warning(f"Neo4j connection failed: {e}. Graph features will be disabled.")
            self.driver = None

    async def generate_cypher(self, objective: str) -> str:
        """NL-to-Cypher generation using LLM."""
        prompt = f"""
        You are a Neo4j Expert. Convert the following natural language architectural objective into a Cypher query.

        SCHEMA:
        - System (id, name, type, cloud, status)
        - DataAsset (id, name, classification)
        - Owner (id, name, department)
        - License (id, name, cost, renewal_date)
        - Policy (id, name, description, severity)
        - PastDecision (id, title, context, decision, justification)

        RELATIONSHIPS:
        - (System)-[:FEEDS]->(System)
        - (System)-[:OWNED_BY]->(Owner)
        - (System)-[:HAS_LICENSE]->(License)
        - (System)-[:USES_DATA]->(DataAsset)
        - (System)-[:MUST_FOLLOW]->(Policy)

        OBJECTIVE: {objective}

        Output ONLY the raw Cypher query. Do not use code blocks.
        """
        response = await self.llm.ainvoke(prompt)
        return response.content.strip().replace("```cypher", "").replace("```", "")

    def execute_query(self, query: str):
        if not self.driver:
            return []
        with self.driver.session() as session:
            try:
                result = session.run(query)
                return [record.data() for record in result]
            except Exception as e:
                logger.error(f"Cypher execution failed: {e}")
                return []

    async def run(self, state):
        objective = state['objective']

        # 1. Structural Retrieval (Neo4j)
        graph_context = ""
        if self.driver:
            cypher = await self.generate_cypher(objective)
            logger.info(f"Generated Cypher: {cypher}")
            graph_results = self.execute_query(cypher)
            graph_context = f"\nGraph Context (Structural): {json.dumps(graph_results)}"

        # 2. Semantic Retrieval (Vector RAG)
        # Assuming vector_service.query is async or needs to be handled
        vector_results = vector_service.query(objective)
        vector_context = f"\nVector Context (Semantic): {json.dumps(vector_results)}"

        state['context'] += graph_context + vector_context
        return state
