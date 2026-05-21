import os
import asyncio
import subprocess
import time
import json

async def run_gen(total_count, model, output_file):
    """
    Runs the generator script. Note: The generator itself now has robust backoff,
    but we still manage batches at the supervisor level for high-volume targets.
    """
    cmd = [
        "python3", "scripts/generate_ea_corpus.py",
        "--total_count", str(total_count),
        "--max_sources", "100",
        "--output", output_file,
        "--append"
    ]
    if model:
        cmd.extend(["--model", model])

    env = os.environ.copy()
    # Ensure backend is in PYTHONPATH
    backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
    env["PYTHONPATH"] = env.get("PYTHONPATH", "") + ":" + backend_path

    process = await asyncio.create_subprocess_exec(
        *cmd,
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return process.returncode, stdout.decode(), stderr.decode()

async def main():
    target = 1000
    current_count = 0
    output_file = "backend/data/synthetic_corpus.jsonl"
    # Leaving model empty uses the base_agent priority (Groq -> SambaNova -> Together)
    model = None

    while True:
        # Check current count
        try:
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    current_count = len(f.readlines())
            else:
                current_count = 0
        except Exception as e:
            print(f"Count check error: {e}")
            current_count = 0

        print(f"--- ArchAI Scaling Supervisor ---")
        print(f"Progress: {current_count}/{target}")

        if current_count >= target:
            print("Target reached! Finalizing Phase 1 Synthetic Generation.")
            break

        batch_size = 50
        print(f"Launching batch of ~{batch_size} samples...")

        rc, out, err = await run_gen(batch_size, model, output_file)

        if rc != 0:
            print(f"Batch completed with errors (rc={rc}). See logs/scaling.log for details.")
            if "429" in out or "429" in err or "rate_limit" in out.lower() or "rate_limit" in err.lower():
                print("Provider Rate Limit hit. Supervisor sleeping for 5 minutes...")
                await asyncio.sleep(300)
            else:
                print("General error. Sleeping for 30 seconds...")
                await asyncio.sleep(30)
        else:
            print(f"Batch completed successfully. Sleeping for 15 seconds to be respectful.")
            await asyncio.sleep(15)

if __name__ == "__main__":
    asyncio.run(main())
