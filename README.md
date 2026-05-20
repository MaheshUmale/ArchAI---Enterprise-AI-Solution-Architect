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

## 🧠 SLM Distillation & Knowledge Foundation
ArchAI is built for Small Language Model (SLM) distillation (3B-7B parameters) using high-quality synthetic data.
- [**Master EA Sources**](./docs/references/MASTER-EA-SOURCES.md): 110+ authoritative EA references (Available locally in `knowledge_base/external_references/`).
- [**Generic Guidance**](./docs/guidance/ARCHAI-GENERIC-GUIDANCE.md): Core architectural philosophy.
- [**Skills Library**](./docs/skills/ARCHAI-GENERIC-SKILLS.md): Explicit architectural capabilities.
- [**Guardrails**](./docs/guardrails/ARCHAI-GUARDRAILS.md): Non-negotiable safety and quality rules.

### 🛠 SLM Distillation Pipeline
ArchAI provides a complete pipeline for high-quality SLM distillation (Continued Pre-training & QLoRA):

1. **Knowledge Ingestion**: Process the master index and local PDFs/EPUBs into structured text.
   ```bash
   # Install processing deps: pip install pdfplumber ebooklib beautifulsoup4 tqdm
   python3 scripts/ingest_master_sources.py --doc_dir "docs/EA_CLOUD_DESIGN PATTERNS/" --max_pages 20
   ```

2. **Synthetic Corpus Generation**: Create high-quality ShareGPT-formatted dialogues using the ingested knowledge and a real teacher LLM (GPT-4o or Claude 3.5 Sonnet).
   ```bash
   # Generates 500-1000 high-quality samples with full ArchAI guidance injection
   python3 scripts/generate_ea_corpus.py --total_count 500 --output backend/data/synthetic_corpus.jsonl

   # For massive scale (2000-5000 examples), increase total_count and max_sources
   python3 scripts/generate_ea_corpus.py --total_count 2000 --max_sources 200
   ```

3. **Dataset Validation & Evaluation**: Ensure the generated corpus is ready for training and score its quality.
   ```bash
   # Validate format and Mermaid syntax
   python3 scripts/train_slm_config/validate_dataset.py backend/data/synthetic_corpus.jsonl

   # Evaluate quality (LLM-as-a-judge)
   python3 scripts/evaluate_slm.py --input backend/data/synthetic_corpus.jsonl
   ```

4. **Training (Axolotl)**: Use the provided configuration for QLoRA fine-tuning.
   ```bash
   # Use Axolotl with the provided config
   accelerate launch -m axolotl.cli.train scripts/train_slm_config/axolotl_qlora.yaml
   ```

3. **Download Local References**: Fetch external source content for offline reference.
   ```bash
   python3 scripts/download_ea_sources.py
   ```
