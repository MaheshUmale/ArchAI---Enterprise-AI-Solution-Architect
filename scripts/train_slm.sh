#!/bin/bash
# ArchAI SLM Training Wrapper for Axolotl

CONFIG_PATH=${1:-"configs/phi35-qlora.yml"}
DATASET_PATH="backend/data/synthetic_corpus_cleaned.json"

echo "🚀 Starting ArchAI SLM Training Pipeline..."

# 1. Advanced Local Validation Pipeline
echo "🛠 Running Local Data Validation & Cleaning Pipeline..."
python3 scripts/filter_diversity.py --input backend/data/synthetic_corpus.jsonl --output backend/data/synthetic_corpus_optimized.json
python3 scripts/clean_boilerplate.py --input backend/data/synthetic_corpus_optimized.json --output backend/data/synthetic_corpus_cleaned.json
python3 scripts/precheck_tokenization.py --input "$DATASET_PATH"

if [ $? -ne 0 ]; then
    echo "❌ Local validation pipeline failed."
    exit 1
fi

# 2. Validate Dataset (Legacy/Syntax Check)
if [ -f "$DATASET_PATH" ]; then
    echo "📊 Running legacy syntax validation: $DATASET_PATH"
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
