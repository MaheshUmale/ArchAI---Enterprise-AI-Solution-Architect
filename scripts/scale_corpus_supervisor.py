import os
import asyncio
import subprocess
import time
import json

async def run_gen(total_count, model, output_file):
    cmd = [
        "python3", "scripts/generate_ea_corpus.py",
        "--total_count", str(total_count),
        "--max_sources", "50",
        "--output", output_file,
        "--model", model,
        "--append"
    ]
    env = os.environ.copy()
    env["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"

    process = await asyncio.create_subprocess_exec(
        *cmd,
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return process.returncode, stdout.decode(), stderr.decode()

async def main():
    target = 800
    current_count = 0
    output_file = "backend/data/synthetic_corpus.jsonl"
    model = "llama-3.1-8b-instant" # Higher TPM usually

    while True:
        # Check current count
        try:
            with open(output_file, 'r') as f:
                current_count = len(f.readlines())
        except:
            current_count = 0

        print(f"Current count: {current_count}/{target}")
        if current_count >= target:
            print("Target reached!")
            break

        print(f"Running generation batch for {model}...")
        # Try to generate 20 at a time
        rc, out, err = await run_gen(20, model, output_file)

        if "rate_limit_exceeded" in out or "rate_limit_exceeded" in err:
            print("Rate limit hit. Sleeping for 60 seconds...")
            await asyncio.sleep(60)
        elif "RESOURCE_EXHAUSTED" in out or "RESOURCE_EXHAUSTED" in err:
            print("Daily quota probably hit. Sleeping for 300 seconds...")
            await asyncio.sleep(300)
        elif rc != 0:
            print(f"Error occurred (rc={rc}). Sleeping for 30 seconds...")
            print(err)
            await asyncio.sleep(30)
        else:
            print("Batch completed successfully. Sleeping for 10 seconds...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
