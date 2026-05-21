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

## 🧠 Phase 3: SLM Optimization & Agentic Loop (Medium Term)
- [ ] **RLHF for Architectural Justification**: Fine-tune the SLM using DPO (Direct Preference Optimization) to favor more evidence-based justifications.
- [ ] **Diagram Syntax Self-Correction**: Teach the SLM to self-correct Mermaid/C4 syntax errors via an iterative agentic loop.
- [ ] **Spec-to-Code Generation**: Extend the Design Agent to generate IaC (Terraform/Pulumi) skeletons from the LLD.

## 🏢 Phase 4: Enterprise Scale & Compliance (Long Term)
- [ ] **Audit & Traceability**: Full cryptographically signed audit logs for every architectural decision.
- [ ] **Multi-Tenant EA Layers**: Support for departmental sub-graphs with inherited global policies.
- [ ] **Hardware Acceleration**: Optimized GGUF/EXL2 quantization for low-latency inference on enterprise edge devices.
