
import subprocess
from pathlib import Path

def generate_pyh_with_claude(json_file: str, pyh_file: str):
    data = Path(json_file).read_text()

    # Build the full prompt
    prompt = f"""
You are an assistant that converts Python AST JSON into an abstracted natural-language AST (.phy).  

## Rules:
- The output must itself be a JSON tree (AST-like).
- Classes, functions, and methods are **anchors**: they must always remain explicit in the structure and never be abstracted away.
- Inside them, you may abstract code into sentences, but keep the nesting deterministic (e.g., class → function → if/else/for → statements).
- **Chunks may be combined** if they are trivial (e.g., multiple simple assignments).
- **Chunks may be split** if they are complex (e.g., recursion, multiple conditions inside if/else).
- Always include `"line_range"` for each abstracted chunk, so UI mapping to the original code is preserved.
- Use `"children"` arrays to represent nesting.
- Output must be valid JSON.

---

## Input Example (AST JSON):
{{
  "metadata": {{
    "original_file": ".\\test1.py",
    "total_chunks": 8,
    "chunking_method": "ast_semantic",
    "timestamp": "2025-09-13T20:26:37.692918"
  }},
  "chunks": {{
    "main": {{
      "id": "main",
      "type": "module",
      "code_blocks": [
        {{
          "type": "chunk_ref",
          "chunk_id": "function_fibonacci",
          "line_range": [1, 10]
        }},
        {{
          "type": "chunk_ref",
          "chunk_id": "if2_block",
          "line_range": [12, 15]
        }}
      ],
      "parent_scope": null
    }},
    "function_fibonacci": {{
      "id": "function_fibonacci",
      "type": "function_definition",
      "code_blocks": [
        {{
          "type": "code",
          "content": ["def fibonacci(n) -> None:"],
          "line_range": [1, 1]
        }},
        {{
          "type": "chunk_ref",
          "chunk_id": "if1_block",
          "line_range": [2, 5]
        }},
        {{
          "type": "code",
          "content": ["fibs = [0, 1]"],
          "line_range": [7, 7]
        }},
        {{
          "type": "chunk_ref",
          "chunk_id": "for1_loop",
          "line_range": [8, 9]
        }},
        {{
          "type": "code",
          "content": ["return fibs"],
          "line_range": [10, 10]
        }}
      ],
      "parent_scope": "main"
    }},
    "if1_block": {{
      "id": "if1_block",
      "type": "if_else_block",
      "code_blocks": [
        {{"type": "chunk_ref", "chunk_id": "if1"}},
        {{"type": "chunk_ref", "chunk_id": "elif1"}}
      ],
      "parent_scope": "function_fibonacci"
    }},
    "if1": {{
      "id": "if1",
      "type": "if_statement",
      "code_blocks": [
        {{
          "type": "code",
          "content": [
            "if n <= 0:",
            "return []",
            "elif n == 1:",
            "return [0]"
          ],
          "line_range": [2, 3]
        }}
      ],
      "parent_scope": "if1_block"
    }},
    "elif1": {{
      "id": "elif1",
      "type": "elif_statement",
      "code_blocks": [],
      "parent_scope": "if1_block"
    }},
    "for1_loop": {{
      "id": "for1_loop",
      "type": "for_loop",
      "code_blocks": [
        {{
          "type": "code",
          "content": ["for i in range(2, n):"],
          "line_range": [8, 8]
        }},
        {{
          "type": "code",
          "content": ["fibs.append(fibs[i-1] + fibs[i-2])"],
          "line_range": [9, 9]
        }}
      ],
      "parent_scope": "function_fibonacci"
    }},
    "if2_block": {{
      "id": "if2_block",
      "type": "if_else_block",
      "code_blocks": [
        {{"type": "chunk_ref", "chunk_id": "if2"}}
      ],
      "parent_scope": "main"
    }},
    "if2": {{
      "id": "if2",
      "type": "if_statement",
      "code_blocks": [
        {{
          "type": "code",
          "content": [
            "if __name__ == \\"__main__\\":",
            "n = 10",
            "sequence = fibonacci(n)",
            "print(f\\"The first {{n}} Fibonacci numbers are: {{sequence}}\\")"
          ],
          "line_range": [12, 15]
        }}
      ],
      "parent_scope": "if2_block"
    }}
  }},
  "relationships": {{
    "execution_flow": ["main"],
    "dependency_graph": {{}}
  }},
  "context_map": {{
    "global_imports": [],
    "global_variables": [],
    "functions": [],
    "classes": []
  }}
}}


---

## Expected Output Example (.phy JSON):
{{
  "phy_chunks": {{
    "main": {{
      "id": "main",
      "type": "module",
      "children": [
        {{
          "id": "function_fibonacci",
          "type": "function_definition",
          "signature": "function fibonacci(takes input n)",
          "children": [
            {{
              "id": "if1_block_abstract",
              "type": "if_else_block",
              "children": [
                {{
                  "id": "if1_abstract",
                  "type": "if_statement",
                  "description": "base case: if n is less than or equal to 0 return an empty list, if n equals 1 return [0]",
                  "line_range": [2, 3]
                }},
                {{
                  "id": "elif1_abstract",
                  "type": "elif_statement",
                  "description": "no additional elif logic",
                  "line_range": [4, 5]
                }}
              ]
            }},
            {{
              "id": "assignment_fibs",
              "type": "assignment",
              "description": "initialize a list fibs with [0, 1]",
              "line_range": [7, 7]
            }},
            {{
              "id": "for1_loop_abstract",
              "type": "for_loop",
              "description": "for each index i from 2 up to n, append the sum of the two previous numbers to the list",
              "line_range": [8, 9]
            }},
            {{
              "id": "return_stmt",
              "type": "return_statement",
              "description": "return the list of Fibonacci numbers",
              "line_range": [10, 10]
            }}
          ]
        }},
        {{
          "id": "if2_abstract",
          "type": "if_statement",
          "description": "when run as main: set n=10, call fibonacci(n), and print the resulting sequence",
          "line_range": [12, 15]
        }}
      ]
    }}
  }}
}}


---

## Task:
Now apply the same abstraction process to the following AST JSON:

{data}

Your output must be only the abstracted .phy JSON, nothing else.
"""


    result = subprocess.run(
        ["claude", prompt],
        capture_output=True,
        text=True
    )

    output = result.stdout.strip()

    if output.startswith("```json") and output.endswith("```"):
        output = output[len("```json"): -len("```")].strip()
    elif output.startswith("'''json") and output.endswith("'''"):
        output = output[len("'''json"): -len("'''")].strip()

    
    if result.returncode != 0:
        print("❌ Error:", result.stderr.strip())
    else:
        Path(pyh_file).write_text(output)   # write cleaned output
        print(f"✅ Generated {pyh_file}")



import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Path to AST JSON file")
    parser.add_argument(
        "-o", "--output",
        help="Path to output .pyh.json file"
    )
    args = parser.parse_args()

    # If no output is given, use input name with .pyh.json
    if args.output is None:
        base = Path(args.input_file).stem  # removes .json
        args.output = f"{base}.pyh.json"

    generate_pyh_with_claude(args.input_file, args.output)
