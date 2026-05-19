# ArchAI SLM Distillation: Pending Tasks & Roadmap

This document outlines the pending tasks and future enhancements for the ArchAI Small Language Model (SLM) distillation pipeline.

## 🛠 High Priority (Pipeline Robustness)
- [x] **Advanced Text Chunking**: Implement semantic or sliding-window chunking in `ingest_master_sources.py`.
- [x] **Header/Footer Removal**: Improve text cleaning logic to identify and remove recurring headers, footers, and page numbers.
- [x] **Deduplication**: Mechanism to detect and remove duplicate chunks using MD5 hashes.
- [x] **Metadata Enrichment**: Extract and store metadata (Title, Author) to improve grounding.

## 🧠 Medium Priority (Data Quality)
- [x] **Dynamic Multi-turn Logic**: Generate dialogues where the assistant handles follow-up challenges.
- [ ] **Mermaid Diagram Validation**: Add a validation step to ensure Mermaid diagrams are syntactically correct.
- [x] **Topic Coverage Balancing**: Even sampling from master index categories.
- [ ] **Skill-Specific Training Sets**: Focused datasets for specific ArchAI skills.

## 🚀 Low Priority (Tooling & UX)
- [x] **Axolotl Wrapper Script**: `scripts/train_slm.sh` to automate validation and training launch.
- [ ] **Evaluation Framework**: Automated comparison suite against Teacher models.
- [ ] **Inference Sandbox**: Gradio/Streamlit UI for offline testing.
- [ ] **DVC Integration**: Manage large artifacts without Git.

## ✅ Completed
- [x] PDF/EPUB extraction support (pdfplumber/ebooklib).
- [x] ShareGPT format conversion.
- [x] Master EA Index ingestion.
- [x] Advanced cleaning & sliding-window chunking.
- [x] Balanced topic sampling.
- [x] Training wrapper script.
- [x] Initial Axolotl QLoRA configuration.
