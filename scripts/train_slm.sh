#!/bin/bash
# ArchAI SLM Training Wrapper for Axolotl

CONFIG_PATH=${1:-"scripts/train_slm_config/axolotl_qlora.yaml"}
DATASET_PATH="backend/data/synthetic_corpus.jsonl"

echo "🚀 Starting ArchAI SLM Training Pipeline..."

# 1. Validate Dataset
if [ -f "$DATASET_PATH" ]; then
    echo "📊 Validating dataset: $DATASET_PATH"
    python3 scripts/train_slm_config/validate_dataset.py "$DATASET_PATH"
    if [ $? -ne 0 ]; then
        echo "❌ Dataset validation failed. Please check your synthetic_corpus.jsonl"
        exit 1
    fi
else
    echo "⚠️ Dataset not found at $DATASET_PATH. Did you run scripts/generate_ea_corpus.py?"
    exit 1
fi

# 2. Check for Axolotl
if ! command -v accelerate &> /dev/null; then
    echo "⚠️ 'accelerate' command not found. Installing Axolotl dependencies..."
    # Note: In a real environment, we'd probably want a specific venv or docker image
    # pip install torch torchvision torchaudio
    # pip install git+https://github.com/OpenAccess-AI-Collective/axolotl
fi

# 3. Launch Training (Optimized for Unsloth + Axolotl)
echo "🏋️ Launching training with Axolotl config: $CONFIG_PATH"
echo "💡 Hardware tip: 24GB+ VRAM (RTX 3090/4090 or A10) recommended for Phi-3.5 4-bit QLoRA."

# Using Unsloth optimized loader via Axolotl
# Note: Ensure you have unsloth installed: pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
accelerate launch -m axolotl.cli.train "$CONFIG_PATH" --unsloth

echo "✅ Training complete or process detached."
