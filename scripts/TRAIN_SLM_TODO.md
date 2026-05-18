# ArchAI SLM Distillation: Pending Tasks & Roadmap

This document outlines the pending tasks and future enhancements for the ArchAI Small Language Model (SLM) distillation pipeline.

## 🛠 High Priority (Pipeline Robustness)
- [ ] **Advanced Text Chunking**: Implement semantic or sliding-window chunking in `ingest_master_sources.py` to process entire books without exceeding LLM context limits.
- [ ] **Header/Footer Removal**: Improve text cleaning logic to identify and remove recurring headers, footers, and page numbers from extracted PDF/EPUB text.
- [ ] **Deduplication**: Implement a mechanism to detect and remove duplicate or highly similar content from the processed documents.
- [ ] **Metadata Enrichment**: Extract and store more detailed metadata (Author, ISBN, Publication Year, Chapter Titles) to improve grounding in generated dialogues.

## 🧠 Medium Priority (Data Quality)
- [ ] **Dynamic Multi-turn Logic**: Update `generate_ea_corpus.py` to generate dialogues iteratively, where the LLM simulates a follow-up conversation based on its own previous responses.
- [ ] **Mermaid Diagram Validation**: Add a validation step to ensure Mermaid diagrams generated in the synthetic corpus are syntactically correct.
- [ ] **Topic Coverage Balancing**: Ensure the corpus generator covers all sections of the `MASTER-EA-SOURCES.md` uniformly to prevent model bias.
- [ ] **Skill-Specific Training Sets**: Create specialized sub-pipelines to generate data focused on specific ArchAI skills (e.g., `tradeoff-matrix` intensive datasets).

## 🚀 Low Priority (Tooling & UX)
- [ ] **Axolotl Wrapper Script**: Create a `scripts/train_slm.sh` script to automate the environment setup and launch training with a single command.
- [ ] **Evaluation Framework**: Develop an automated evaluation suite to compare SLM performance against the "Teacher" model (GPT-4o/Claude 3.5) using architectural benchmarks.
- [ ] **Inference Sandbox**: Add a simple Gradio or Streamlit UI to test the distilled SLM's architectural reasoning capabilities offline.
- [ ] **DVC Integration**: Use Data Version Control (DVC) to manage the large `processed_docs.json` and `synthetic_corpus.jsonl` files without committing them to Git.

## ✅ Completed
- [x] PDF/EPUB extraction support.
- [x] ShareGPT format conversion.
- [x] Master EA Index ingestion.
- [x] Basic dataset validation script.
- [x] Initial Axolotl QLoRA configuration.
- [x] SLM Distillation Guide in README/Setup.
