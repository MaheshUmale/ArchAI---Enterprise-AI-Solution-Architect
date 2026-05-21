import os
import sys
import argparse
import logging
import asyncio
from typing import List, Dict

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

from dotenv import load_dotenv
load_dotenv()
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

try:
    import gradio as gr
    from app.agents.base_agent import get_llm
except ImportError as e:
    print(f"Error: Missing dependencies. Run: pip install -r scripts/requirements_slm.txt")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_response(prompt: str, model_type: str, temperature: float):
    """Generates a response from the selected model."""
    try:
        # Configure model based on selection
        if model_type == "Local SLM (Ollama/Local)":
            os.environ["USE_LOCAL_LLM"] = "true"
            llm = get_llm(temperature=temperature)
        elif model_type == "Teacher (Groq/Claude)":
            os.environ["USE_LOCAL_LLM"] = "false"
            llm = get_llm(temperature=temperature)
        else:
            # Default fallback
            llm = get_llm(temperature=temperature)

        response = await llm.ainvoke(prompt)
        return response.content
    except Exception as e:
        logger.error(f"Inference failed for {model_type}: {e}")
        return f"Error: {str(e)}"

def sandbox_ui():
    with gr.Blocks(title="ArchAI Inference Sandbox") as demo:
        gr.Markdown("# 🏛 ArchAI Inference Sandbox")
        gr.Markdown("Compare your fine-tuned **Phi-3.5 Student** with the **Teacher LLM**.")

        with gr.Row():
            with gr.Column():
                prompt_input = gr.Textbox(
                    label="Architectural Objective",
                    placeholder="e.g., Design a real-time data ingestion pipeline for IoT sensors...",
                    lines=5
                )
                temp_slider = gr.Slider(minimum=0.0, maximum=1.0, value=0.2, step=0.1, label="Temperature")
                run_btn = gr.Button("Generate Designs", variant="primary")

        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🎓 Student (Local SLM)")
                student_output = gr.Textbox(label="Phi-3.5 Output", lines=15)

            with gr.Column():
                gr.Markdown("### 🍎 Teacher (Cloud API)")
                teacher_output = gr.Textbox(label="Teacher Output", lines=15)

        async def compare_models(prompt, temp):
            # Run both in parallel
            student_task = generate_response(prompt, "Local SLM (Ollama/Local)", temp)
            teacher_task = generate_response(prompt, "Teacher (Groq/Claude)", temp)

            student_res, teacher_res = await asyncio.gather(student_task, teacher_task)
            return student_res, teacher_res

        run_btn.click(
            fn=compare_models,
            inputs=[prompt_input, temp_slider],
            outputs=[student_output, teacher_output]
        )

    return demo

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ArchAI Inference Sandbox UI")
    parser.add_argument("--share", action="store_true", help="Generate a public link")
    parser.add_argument("--port", type=int, default=7860, help="Gradio port")

    args = parser.parse_args()

    demo = sandbox_ui()
    demo.launch(share=args.share, server_port=args.port)
