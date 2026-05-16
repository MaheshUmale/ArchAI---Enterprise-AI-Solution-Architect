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
