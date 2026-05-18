import json
import os
import sys

def validate_sharegpt_jsonl(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.")
        return False

    print(f"Validating {filepath}...")
    valid_count = 0
    error_count = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            try:
                data = json.loads(line)
                if "conversations" not in data:
                    print(f"Line {i}: Missing 'conversations' key.")
                    error_count += 1
                    continue

                convs = data["conversations"]
                if not isinstance(convs, list):
                    print(f"Line {i}: 'conversations' must be a list.")
                    error_count += 1
                    continue

                if len(convs) == 0:
                    print(f"Line {i}: 'conversations' list is empty.")
                    error_count += 1
                    continue

                for j, msg in enumerate(convs):
                    if "from" not in msg or "value" not in msg:
                        print(f"Line {i}, Msg {j}: Missing 'from' or 'value' key.")
                        error_count += 1
                        continue
                    if msg["from"] not in ["human", "gpt", "system"]:
                        print(f"Line {i}, Msg {j}: Unknown sender '{msg['from']}'. Expected 'human', 'gpt', or 'system'.")
                        error_count += 1
                        continue

                valid_count += 1
            except json.JSONDecodeError as e:
                print(f"Line {i}: Invalid JSON - {e}")
                error_count += 1

    print("\n--- Validation Result ---")
    print(f"Total entries: {valid_count + error_count}")
    print(f"Valid entries: {valid_count}")
    print(f"Errors found:  {error_count}")

    return error_count == 0

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "backend/data/synthetic_corpus.jsonl"
    success = validate_sharegpt_jsonl(path)
    sys.exit(0 if success else 1)
