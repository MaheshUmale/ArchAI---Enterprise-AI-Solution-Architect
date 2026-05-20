# ArchAI SLM Distillation: Pending Tasks & Roadmap

This document outlines the pending tasks and future enhancements for the ArchAI Small Language Model (SLM) distillation pipeline.

## 🛠 High Priority (Pipeline Robustness)
- [x] **Advanced Text Chunking**: Implement semantic or sliding-window chunking in `ingest_master_sources.py`.
- [x] **Header/Footer Removal**: Improve text cleaning logic to identify and remove recurring headers, footers, and page numbers.
- [x] **Deduplication**: Mechanism to detect and remove duplicate chunks using MD5 hashes.
- [x] **Metadata Enrichment**: Extract and store metadata (Title, Author) to improve grounding.

## 🧠 Medium Priority (Data Quality)
- [x] **Dynamic Multi-turn Logic**: Generate dialogues where the assistant handles follow-up challenges.
- [x] **Mermaid Diagram Validation**: Basic syntax check for Mermaid blocks in `validate_dataset.py`.
- [x] **Topic Coverage Balancing**: Even sampling from master index categories.
- [x] **Skill-Specific Training Sets**: `--skill` argument in `generate_ea_corpus.py` to focus on specific capabilities.

## 🚀 Low Priority (Tooling & UX)
- [x] **Axolotl Wrapper Script**: `scripts/train_slm.sh` to automate validation and training launch.
- [x] **Evaluation Framework**: Skeleton `scripts/evaluate_slm.py` using LLM-as-a-Judge.
- [ ] **Inference Sandbox**: Gradio/Streamlit UI for offline testing.
- [ ] **DVC Integration**: Manage large artifacts without Git.

## ✅ Completed
- [x] **Design Patterns Ingestion**: Integrated 56 new sources from `Architectural Design Patterns.md`.
- [x] **Multi-Provider LLM Support**: Native support for Groq and Gemini in distillation pipeline.
- [x] **High-Volume Scaling**: Established automated supervisor for corpus expansion (220+ samples generated).
- [x] PDF/EPUB extraction support (pdfplumber/ebooklib).
- [x] ShareGPT format conversion.
- [x] Master EA Index ingestion.
- [x] Advanced cleaning & sliding-window chunking.
- [x] Balanced topic sampling.
- [x] Training wrapper script.
- [x] Skill-specific generation.
- [x] Initial Axolotl QLoRA configuration.
- [x] Mermaid validation.
- [x] Evaluation framework skeleton.
