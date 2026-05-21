# ArchAI SLM Training & Distillation Guide

This guide outlines the process of training the ArchAI Small Language Model (SLM) using the synthetic corpus generated from authoritative Enterprise Architecture sources.

## 🔄 The Distillation Workflow

ArchAI uses a multi-stage distillation process to transfer knowledge from a massive Teacher Model (Claude 3.5 Sonnet / GPT-4o) into a surgical 3.8B parameter SLM (Phi-3.5-mini).

### 1. Continued Pre-training (CPT)
*Optional for domain specialization.*
If the SLM lacks basic architectural vocabulary, we perform CPT on raw chunks from `processed_docs.json` to ground the model in the enterprise domain.

### 2. Supervised Fine-Tuning (SFT) / QLoRA
The core of our distillation. We use the multi-turn dialogues in `synthetic_corpus.jsonl` to teach the model:
- **ArchAI Philosophy**: "Think Architecturally First".
- **Skills**: Trade-off matrices, reuse-first evaluation, and C4 diagramming.
- **Guardrails**: Professionalism, safety, and evidence-based justification.

We use **Axolotl + Unsloth** for 4-bit Quantized LoRA (QLoRA) to significantly reduce VRAM requirements while maintaining performance.

### 3. Zero-Cost / Local Validation
To minimize training noise and API costs, we move data prep and evaluation to local scripts:
- **`scripts/filter_diversity.py`**: Uses embedding-based cosine similarity to remove redundant dialogues.
- **`scripts/clean_boilerplate.py`**: Prunes systemic LLM artifacts and "phrasing traps".
- **`scripts/precheck_tokenization.py`**: Validates format and sequence length locally before touching expensive compute.

### 4. Quantization & Export
Post-training, the model is merged and quantized into **GGUF** (for local CPU/GPU execution) or **EXL2** (for high-throughput inference) formats.

## 🛠 Setup & Execution

### Prerequisites
- **Hardware**: Single GPU with 24GB+ VRAM (RTX 3090, 4090, or A10) is highly recommended.
- **Environment**: CUDA 12.x and PyTorch 2.x.

### Training Steps
1. **Generate Data**: Run `scripts/generate_ea_corpus.py` using fallback providers (SambaNova/Together) to build your raw corpus.
2. **Clean & Validate**: Run the local validation pipeline:
   ```bash
   python3 scripts/filter_diversity.py
   python3 scripts/clean_boilerplate.py
   python3 scripts/precheck_tokenization.py
   ```
3. **Launch (Local/Cloud)**:
   - For Cloud: Upload `synthetic_corpus_cleaned.json` to [scripts/train_phi35_unsloth.ipynb](scripts/train_phi35_unsloth.ipynb).
   - For Local: Run `bash scripts/train_slm.sh` (Requires 16GB+ VRAM).

## 📊 Evaluation
After training, evaluate the model's performance using `scripts/evaluate_slm.py` to compare its responses against the teacher model's standards.

## 🚀 Deployment
Deploy the fine-tuned SLM using tools like **vLLM**, **Ollama**, or **LM Studio** for local architectural assistance.
