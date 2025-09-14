#!/usr/bin/env python3
"""
apply_diff_with_claude.py
Apply user edits (captured as diffs) back onto original Python code using Claude SDK.
"""

import json
from pathlib import Path
import argparse
import anthropic  # Claude SDK
import subprocess


def apply_diff_to_file(diff_file: str, original_py: str, output_py: str):
    # Load diff + original code
    diff_text = Path(diff_file).read_text()
    try:
        diff_data = json.loads(diff_text)
    except json.JSONDecodeError:
        print("❌ Diff file is not valid JSON. Ensure diff_analyzer wrote proper JSON.")
        return

    original_code = Path(original_py).read_text()

    # Prompt with strong rules + example
    prompt = f"""
You are an assistant that applies **abstracted diffs** back onto original Python code.

## Context
- The user edits Python code indirectly by changing a natural-language `.pyh.json`.
- We now have a diff JSON (`diff.json`) describing:
  - Which AST nodes or sections changed.
  - What was added/removed/modified in plain language.
- Your job: rewrite the original Python file so it **fully reflects the user’s intended changes**.

## Rules
- Strictly follow the changes mentioned in the diff and make changes to the referred file according to the lines specified.
- Identify any affected files or functions in the repo from these changes. If necessary, make any required changes to them.
- Be very careful. Only change the code that needs to be changed according to the diffs.
- Preserve all unaffected code exactly as-is.
- Apply every diff faithfully:
  - If a constructor gains a new parameter → add it everywhere (signature + assignments).
  - If a method changes logic → update its implementation accordingly.
  - If a class/method is removed → remove it.
- If diff implies major restructuring, rewrite the file consistently.
- Keep formatting PEP8-compliant.
- Do not output explanations, only code.

---

Actual Diff

{json.dumps(diff_data, indent=2)}

File to change:
 "metadata": {{
    "source_file": "/Users/krishnapagrut/Developer/hcli/test.py"
  }}

Change the python files and then
Return all the paths and changes made as comments in the python file.
"""

    # Call Claude CLI
    result = subprocess.run(
        ["claude", prompt],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("❌ Claude CLI error:", result.stderr.strip())
        return

    output = result.stdout.strip()

    # Strip markdown fences if Claude added them
    if output.startswith("```python") and output.endswith("```"):
        output = output[len("```python"): -len("```")].strip()

    Path(output_py).write_text(output)
    print(f"✅ Updated file written to {output_py}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply diff back onto Python code using Claude")
    parser.add_argument("diff", help="Diff JSON file (from diff_analyzer)")
    parser.add_argument("original", help="Original Python file")
    parser.add_argument("-o", "--output", help="Output updated Python file")
    args = parser.parse_args()

    if args.output is None:
        args.output = args.original.replace(".py", ".updated.py")

    apply_diff_to_file(args.diff, args.original, args.output)
