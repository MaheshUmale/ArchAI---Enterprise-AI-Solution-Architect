# ArchAI Project Roadmap

This document outlines the strategic phases for evolving ArchAI from an MVP into a production-grade Enterprise AI Architect.

## ✅ Phase 1: Knowledge Foundation & Distillation (Complete)
- [x] **Master EA Index**: Indexed 115+ authoritative sources.
- [x] **Pattern Ingestion**: Automated processing of cloud design patterns.
- [x] **Multi-Agent Core**: Established LangGraph orchestration.
- [x] **Graph Schema Deepening**: Support for Licenses, Owners, Policies, and Decisions.
- [x] **SLM Distillation Ecosystem**:
    - Zero-cost generation using Groq/SambaNova.
    - Local data validation (Diversity, Boilerplate, Tokenization).
    - Unsloth-optimized 4-bit QLoRA training for Phi-3.5.
    - Comparative Evaluation & KG Grounding checks.

## ✅ Phase 2: Graph-RAG Deepening (Complete)
- [x] **Dynamic Ontology Mapping**: LLM-based extraction of Neo4j nodes from unstructured content (`scripts/extract_entities.py`).
- [x] **Dynamic Cypher Reasoning**: Knowledge Agent powered by NL-to-Cypher generation for multi-hop graph queries.
- [x] **Past Decision Injection**: Seeded Knowledge Graph with industry-standard HLD patterns for Case-Based Reasoning (`scripts/seed_past_decisions.py`).
- [x] **Hybrid Retrieval**: Coordination between structural graph lookups and semantic vector search.

## ✅ Phase 3: SLM Optimization & Agentic Loop (Complete)
- [x] **Justification Alignment**: Implementation of DPO pair generation for evidence-based fine-tuning (`scripts/generate_dpo_pairs.py`).
- [x] **Diagram Self-Correction**: Integrated `DiagramAgent` and validation loop in LangGraph for 100% syntactically correct Mermaid.
- [x] **Spec-to-Code Generation**: Foundation for IaC generation (Terraform) implemented in `backend/app/tools/iac_generator.py`.

## ✅ Phase 4: Enterprise Scale & Compliance (Complete)
- [x] **Audit & Traceability**: Cryptographically signed SHA-256 audit logs for architectural decisions.
- [x] **Multi-Tenant EA Layers**: Departmental scoping for Knowledge Graph queries and context.
- [x] **SLM Portability**: Optimized training pipeline for local and cloud-hybrid execution.

## 🎨 Phase 5: Enterprise Portal & Visualization (Future)
- [ ] **Interactive Mermaid Rendering**: Native browser rendering of system architecture diagrams.
- [ ] **IaC Workbench**: Direct export and preview of generated Terraform skeletons.
- [ ] **Collaboration Engine**: Multi-user design reviews and threading on HLD artifacts.
