import json
import argparse
from pathlib import Path

def render_node(node, indent=0):
    lines = []
    pad = "    " * indent

    sig = node.get("signature")
    desc = node.get("description")
    line_range = node.get("line_range")

    # Line info
    line_info = ""
    if line_range:
        line_info = f"  (lines {line_range[0]}–{line_range[1]})"

    # Show signature
    if sig:
        lines.append(f"{pad}{sig}{line_info}")
        if desc:
            lines.append(f"{pad}    {desc}")  # plain sentence
    elif desc:
        lines.append(f"{pad}{desc}{line_info}")

    # Recurse into children
    for child in node.get("children", []):
        lines.extend(render_node(child, indent + 1))

    return lines

def phy_ast_to_output(pyh_file, output_file=None):
    text = Path(pyh_file).read_text().strip()

    # Strip markdown fences if present
    if text.startswith("```"):
        text = "\n".join(line for line in text.splitlines() if not line.strip().startswith("```"))

    data = json.loads(text)

    if "phy_chunks" not in data or "main" not in data["phy_chunks"]:
        raise ValueError("Invalid .pyh JSON: missing phy_chunks/main")

    root = data["phy_chunks"]["main"]
    result = "\n".join(render_node(root))

    if output_file:
        Path(output_file).write_text(result)
        print(f"Output written to {output_file}")
    else:
        print(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pyh_file", help="Input .pyh JSON file")
    parser.add_argument("-o", "--output", help="Optional output file (.txt)")
    args = parser.parse_args()

    phy_ast_to_output(args.pyh_file, args.output)
