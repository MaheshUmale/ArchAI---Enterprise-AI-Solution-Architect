# ArchAI

### Latest Updates: Architectural Design Patterns Ingestion
- **New Sources**: Ingested 56 high-value design pattern sources from `Architectural Design Patterns.md`.
- **Corpus Expansion**: Scaled synthetic training corpus to 220+ high-quality architectural dialogues using Groq (`llama-3.3-70b-versatile`).
- **Groq Support**: Added native support for Groq models in the backend agent factory for high-throughput distillation.
- **Evaluation**: SLM evaluation shows per-sample diversity of 0.60 and strong adherence to ArchAI surgical architectural skills.





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

## 🧠 SLM Distillation & Knowledge Foundation
ArchAI is built for Small Language Model (SLM) distillation (3B-7B parameters) using high-quality synthetic data.
- [**Master EA Sources**](./docs/references/MASTER-EA-SOURCES.md): 110+ authoritative EA references (Available locally in `knowledge_base/external_references/`).
- [**Generic Guidance**](./docs/guidance/ARCHAI-GENERIC-GUIDANCE.md): Core architectural philosophy.
- [**Skills Library**](./docs/skills/ARCHAI-GENERIC-SKILLS.md): Explicit architectural capabilities.
- [**Guardrails**](./docs/guardrails/ARCHAI-GUARDRAILS.md): Non-negotiable safety and quality rules.

### 🛠 SLM Distillation Pipeline
ArchAI provides a complete pipeline for high-quality SLM distillation (Continued Pre-training & QLoRA), optimized for cost-control and performance:

1. **Knowledge Ingestion**: Process the master index and local PDFs/EPUBs into structured text.
   ```bash
   # Install processing deps: pip install pdfplumber ebooklib beautifulsoup4 tqdm
   python3 scripts/ingest_master_sources.py --doc_dir "docs/EA_CLOUD_DESIGN_PATTERNS/" --max_pages 20
   ```

2. **Synthetic Corpus Generation**: Create high-quality ShareGPT-formatted dialogues using free-tier providers (Groq, SambaNova, Together AI).
   ```bash
   # Generates high-quality samples with full ArchAI guidance injection
   # Robust exponential backoff handles rate-limits automatically.
   python3 scripts/generate_ea_corpus.py --total_count 1000 --output backend/data/synthetic_corpus.jsonl
   ```

3. **Zero-Cost Validation & Evaluation**: Optimize and validate your dataset locally (no API cost).
   ```bash
   # Filter semantic duplicates and redundant dialogues
   python3 scripts/filter_diversity.py

   # Remove LLM phrasing traps and clean boilerplate
   python3 scripts/clean_boilerplate.py

   # Local tokenization and multi-turn sequence pre-check
   python3 scripts/precheck_tokenization.py
   ```

4. **Training (Axolotl + Unsloth)**: Use the optimized [phi35-qlora.yml](./configs/phi35-qlora.yml) for memory-efficient 4-bit QLoRA.
   - **Cloud Training**: Use the [Zero-Cost Training Notebook](./scripts/train_phi35_unsloth.ipynb) on Google Colab (T4) or Kaggle (Dual T4).
   - **Local Training**: Requires 16GB+ VRAM.
   ```bash
   # Launch training with local validation pre-check
   bash scripts/train_slm.sh
   ```

3. **Download Local References**: Fetch external source content for offline reference.
   ```bash
   python3 scripts/download_ea_sources.py
   ```
