import subprocess
from pathlib import Path

def generate_pyh_with_claude(json_file: str, pyh_file: str):
    data = Path(json_file).read_text()

    # Build the full prompt
    prompt = f"""
Convert the following JSON AST into an abstract `.pyh` file.

Rules:
- Replace "def" with "function".
- After the signature, describe the function in ONE plain English sentence.
- Keep it simple, e.g., "Find a task by title in the list or its subtasks, otherwise return none".
- Indent correctly.

JSON:
{data}
"""

    # Call Claude CLI in one-shot mode
    result = subprocess.run(
        ["claude", prompt],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("❌ Error:", result.stderr.strip())
    else:
        Path(pyh_file).write_text(result.stdout.strip())
        print(f"✅ Generated {pyh_file}")


if __name__ == "__main__":
    generate_pyh_with_claude("test_chunked.json", "test.pyh")
