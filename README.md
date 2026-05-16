# ArchAI - Enterprise AI Solution Architect

AI-powered Solution Architect that deeply understands your organization's tools, policies, licenses, and constraints.

## MVP Features
- Enterprise Knowledge Graph + RAG
- Agentic workflow (Orchestrator + 6 specialist agents)
- Justified HLD generation with diagrams and trade-off matrices
- Strong guardrails (reuse, compliance, cost, hallucination)

## Tech Stack
- Backend: FastAPI + LangGraph + Neo4j + PostgreSQL
- Frontend: Next.js 15
- LLMs: Azure OpenAI + Claude 3.5

## Quick Start
```bash
docker-compose up -d

cd backend && uv sync && uv run uvicorn app.main:app --reload
```

=====================
## Project Structure
See docs/architecture/ for details.
text---

### **2. Docker Setup**

#### `docker-compose.yml`
```yaml
version: '3.9'

services:
  neo4j:
    image: neo4j:5.20-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/password123
      NEO4J_PLUGINS: '["apoc"]'
    volumes:
      - neo4j_data:/data

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: archai
      POSTGRES_USER: archai
      POSTGRES_PASSWORD: archai123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=password123
      - DATABASE_URL=postgresql://archai:archai123@postgres:5432/archai
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - neo4j
      - postgres

volumes:
  neo4j_data:
  postgres_data:
  ```

3. Backend Core Files
backend/requirements.txt
txtfastapi==0.115.0
uvicorn[standard]==0.30.0
langgraph==0.2.0
langchain==0.3.0
langchain-openai==0.2.0
langchain-community==0.3.0
neo4j==5.25.0
pinecone-client==5.0.0
psycopg2-binary==2.9.10
pydantic==2.9.0
python-dotenv==1.0.1
httpx==0.27.0
pandas==2.2.0
openpyxl==3.1.5
backend/app/core/config.py
Pythonfrom pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ArchAI"
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password123"
    OPENAI_API_KEY: str
    CLAUDE_API_KEY: str | None = None
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
backend/app/main.py
Pythonfrom fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "ArchAI MVP is running 🚀"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

4. Knowledge Layer
backend/app/knowledge/graph_schema.py
PythonKNOWLEDGE_GRAPH_SCHEMA = """
// Core Nodes
CREATE CONSTRAINT system_id IF NOT EXISTS FOR (s:System) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT data_asset_id IF NOT EXISTS FOR (d:DataAsset) REQUIRE d.id IS UNIQUE;

// Relationships
CREATE CONSTRAINT interface_id IF NOT EXISTS FOR ()-[r:FEEDS]-() REQUIRE r.id IS UNIQUE;
"""
backend/app/knowledge/ingestion.py
Pythonimport json
from neo4j import GraphDatabase
from app.core.config import settings

class KnowledgeIngestion:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def ingest_json(self, data: dict):
        with self.driver.session() as session:
            # Ingest Systems
            for sys in data.get("systems", []):
                session.run("""
                    MERGE (s:System {id: $id})
                    SET s.name = $name, s.type = $type, s.cloud = $cloud, 
                        s.owner = $owner, s.status = $status
                """, **sys)
            
            # Add more entity ingestion (DataAsset, Interface, License, Policy, etc.)

5. Pydantic Models (Artifacts)
backend/app/models/artifacts.py
Pythonfrom pydantic import BaseModel, Field
from typing import List, Dict, Optional

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
    risks_and_mitigations: List[Dict]
    compliance_summary: str
    confidence_score: float = Field(ge=0, le=100)

class DesignRequest(BaseModel):
    objective: str
    additional_context: Optional[str] = None
    constraints: Optional[Dict] = None

6. Agents Definitions
backend/app/agents/base_agent.py
Pythonfrom langchain_openai import ChatOpenAI
from app.core.config import settings

def get_llm(temperature=0.0, model="gpt-4o"):
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=settings.OPENAI_API_KEY
    )
backend/app/agents/orchestrator.py
Pythonfrom langgraph.graph import StateGraph, END
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

7. Core Workflow (LangGraph)
backend/app/graph/workflow.py
Pythonfrom langgraph.graph import StateGraph, END
from app.agents.base_agent import get_llm
from app.models.artifacts import HLDDocument

llm = get_llm()

def orchestrator_node(state):
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
# Add more nodes: knowledge_retrieval, reuse_check, tradeoff_analysis, design_generation, review

# Compile
graph = workflow.compile()

8. API Routes
backend/app/api/routes.py
Pythonfrom fastapi import APIRouter
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

Next Recommended Steps
You now have the core foundation ready.
I will generate the next batch immediately if you want:

Full LangGraph multi-agent implementation with all 6 agents
Complete Knowledge Graph queries + RAG service
Sample EA data (JSON)
Frontend basic structure (Next.js)
Guardrail implementations
