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

### 3. Quantization & Export
Post-training, the model is merged and quantized into **GGUF** (for local CPU/GPU execution) or **EXL2** (for high-throughput inference) formats.

## 🛠 Setup & Execution

### Prerequisites
- **Hardware**: Single GPU with 24GB+ VRAM (RTX 3090, 4090, or A10) is highly recommended.
- **Environment**: CUDA 12.x and PyTorch 2.x.

### Training Steps
1. **Prepare Data**: Ensure `backend/data/synthetic_corpus.jsonl` is populated.
2. **Validate**: Run `python3 scripts/train_slm_config/validate_dataset.py` to check for format issues.
3. **Launch**:
   ```bash
   bash scripts/train_slm.sh
   ```

## 📊 Evaluation
After training, evaluate the model's performance using `scripts/evaluate_slm.py` to compare its responses against the teacher model's standards.

## 🚀 Deployment
Deploy the fine-tuned SLM using tools like **vLLM**, **Ollama**, or **LM Studio** for local architectural assistance.
