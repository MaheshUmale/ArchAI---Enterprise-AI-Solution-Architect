# ArchAI - Enterprise AI Solution Architect

ArchAI is an AI-powered Solution Architect that deeply understands your organization's tools, policies, licenses, and constraints. It enables users to provide objectives and receive justified, organization-aware High-Level Designs (HLD) and Low-Level Designs (LLD) with full traceability and reuse enforcement.

## 🚀 MVP Vision
"Give objectives → Get justified, organization-aware HLD/LLD with full traceability and reuse enforcement."

## ✨ Key Features
- **Enterprise Knowledge Graph + Vector RAG**: Ingests EA data (JSON/Excel) to build a deep understanding of the landscape.
- **Multi-Agent Orchestration**: Powered by LangGraph, ArchAI uses specialized agents for design, compliance, cost-analysis, and review.
- **Justified HLD Generation**: Produces C4-inspired Mermaid diagrams, decision matrices, and comprehensive documentation.
- **Strong Guardrails**: Enforces reuse-before-buy policies, security compliance, and cost-effectiveness.
- **Human-in-the-Loop**: Interactive chat and iterative design refinement.

## 🛠 Tech Stack
- **Backend**: Python 3.11+, FastAPI
- **Agent Orchestration**: LangGraph
- **LLMs**: Azure OpenAI (GPT-4o) & Claude 3.5 Sonnet
- **Knowledge Layer**: Neo4j (Graph), Pinecone/Chroma (Vector), PostgreSQL
- **Frontend**: Next.js 15 (App Router), Tailwind CSS, shadcn/ui
- **Diagrams**: Mermaid, React Flow
- **Observability**: LangSmith

## 📁 Project Structure
```text
archai-mvp/
├── backend/
│   ├── app/
│   │   ├── agents/               # Specialist agent definitions
│   │   ├── graph/                # LangGraph stateful workflows
│   │   ├── tools/                # Custom architectural tools
│   │   ├── knowledge/            # Graph & Vector RAG services
│   │   ├── api/                  # FastAPI endpoints
│   │   ├── models/               # Pydantic schemas for artifacts
│   │   └── core/                 # Config & Guardrails
│   ├── data/                     # Sample data for testing
│   └── tests/                    # Backend test suite
├── frontend/                     # Next.js web application
├── docs/
│   ├── agents/                   # Detailed agent specifications
│   ├── architecture/             # System design docs
│   └── prompts/                  # LLM prompt templates
├── knowledge_base/               # Sample EA data (JSON/Excel)
├── docker-compose.yml            # Local infrastructure (Neo4j, Postgres)
└── README.md
```

## 🚦 Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js & npm (for frontend)

### Quick Start
1. **Infrastructure**: Start the database services.
   ```bash
   docker-compose up -d
   ```

2. **Backend**: Install dependencies and run the API.
   ```bash
   cd backend
   pip install -r requirements.txt
   # Ensure .env is configured with API keys
   uvicorn app.main:app --reload
   ```

3. **Frontend**: Launch the web interface.
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 🤖 Agent Specialists
ArchAI utilizes 6 specialized agents:
1. **Orchestrator**: Leads the design process and synthesizes the final package.
2. **Knowledge Agent**: The "Enterprise Memory" retrieving facts from Neo4j.
3. **Reuse & Compliance**: Enforces architectural standards and security.
4. **Trade-off & Cost**: Analyzes TCO and provides decision matrices.
5. **Design Agent**: Generates diagrams and technical skeletons.
6. **Reviewer**: Provides quality assurance and simulates cross-team critique.

See `docs/agents/` for more details.

## 📖 Documentation
- [**User Guide**](./docs/USER_GUIDE.md): How to use ArchAI effectively.
- [**Setup Guide**](./docs/SETUP_GUIDE.md): Technical instructions for developers.
- [**Agent Specifications**](./docs/agents/): Detailed roles for each AI agent.
