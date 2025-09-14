"""
Apply Changes Demo - Uses Claude to apply changes from changes.json to test.py
This demonstrates how to use Claude Code SDK to apply specific code changes.
"""

import asyncio
import json
import os
import sys
from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock, CLINotFoundError, ProcessError
from claude_config import get_config_for_use_case
from pathlib import Path


async def apply_changes_from_json(file_stem: str):
    """Apply changes from changes.json to the target Python file using Claude"""
    try:
        # Load changes.json
        with open("changes.json", "r") as f:
            changes_data = json.load(f)

        # Resolve AST file path
        ast_path = changes_data.get("ast_file")
        if not ast_path:
            raise ValueError("❌ ast_file missing from changes.json")

        with open(ast_path, "r") as f:
            ast_data = json.load(f)

        # Resolve source_file safely
        metadata = ast_data.get("metadata", {})
        print("DEBUG: metadata =", metadata)

        # Support both keys: source_file and source_py
        source_file = (
            metadata.get("source_file")
            or metadata.get("source_py")
            or f"{file_stem}.py"
        )

        # Normalize AST → .py if necessary
        if source_file.endswith(".ast.pyh.json"):
            source_file = source_file.replace(".ast.pyh.json", ".py")

        print(f"DEBUG: Using source_file = {source_file}")

        # Load Claude config
        config = get_config_for_use_case("development")

        # Extract just the line numbers and changes
        changes_summary = "Changes to apply:\n"
        for i, change in enumerate(changes_data["changes"], 1):
            line_range = change.get("line_range") or []
            original = change.get("original_content", "")
            modified = change.get("modified_content", "")
            if len(line_range) == 2:
                line_info = f"Lines {line_range[0]}-{line_range[1]}"
            elif len(line_range) == 1:
                line_info = f"Line {line_range[0]}"
            else:
                line_info = "(unspecified lines)"
            changes_summary += (
                f"{i}. Lines{line_info}: {original} → {modified}\n"
            )

        # Create the prompt in readable multi-line format
        prompt_template = f"""You are an assistant that applies abstracted diffs back onto original Python code.

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

{changes_summary}

Diff file to change (other referenced files can be changed as well):
 "metadata": {{
    "source_file": "{source_file}"
  }}

### Output Format
For each modified file, return:
FILE: <path/to/file>
```python
<full updated file content>
After all modified files, output:
{{ "modified_files": ["list", "of", "changed", "file_paths"] }}

Return all the paths and changes made."""

        # Convert to single line for CLI compatibility
        prompt = prompt_template.replace('\n', ' ').replace('  ', ' ').strip()
        
        print("Sending request to Claude...")
        print("Changes to apply:")
        for i, change in enumerate(changes_data['changes'], 1):
            print(f"  {i}. {change['node_id']}: {change['original_content']} -> {change['modified_content']}")
        
        print("\nClaude's response:")
        print("-" * 50)

        print(prompt)
        
        modified_files = []

        async for message in query(prompt=prompt, options=config):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text = block.text.strip()
                        print(text)
                        if text.startswith("{") and "modified_files" in text:
                            try:
                                data = json.loads(text)
                                modified_files = data.get("modified_files", [])
                            except Exception:
                                pass

        return modified_files

                        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("Make sure changes.json and test.py exist in the current directory")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        print("Make sure changes.json is valid JSON")
    except CLINotFoundError:
        print("❌ Claude Code CLI not found")
        print("Install it with: npm install -g @anthropic-ai/claude-code")
    except ProcessError as e:
        print(f"❌ Process error: {e}")
        print("Check that Claude Code CLI is properly configured")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Check your setup and try again")


async def analyze_changes_structure():
    """Analyze the structure of changes.json"""
    print("\n=== Analyzing changes.json Structure ===")
    
    try:
        with open('changes.json', 'r') as f:
            changes_data = json.load(f)
        
        print(f"Total changes: {changes_data['total_changes']}")
        print(f"Files involved: {changes_data['file1']}, {changes_data['file2']}")
        print(f"AST file: {changes_data['ast_file']}")
        
        print("\nDetailed changes:")
        for i, change in enumerate(changes_data['changes'], 1):
            print(f"\n{i}. {change['node_id']}")
            print(f"   Type: {change['node_type']}")
            print(f"   Signature: {change['signature']}")
            print(f"   Description: {change['description']}")
            print(f"   Line range: {change['line_range']}")
            print(f"   Change type: {change['change_type']}")
            print(f"   Original: {change['original_content']}")
            print(f"   Modified: {change['modified_content']}")
            
    except FileNotFoundError:
        print("❌ changes.json not found in current directory")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in changes.json: {e}")
    except Exception as e:
        print(f"❌ Error analyzing changes: {e}")


async def create_updated_test_file():
    """Create an updated version of test.py with the changes applied"""
    print("\n=== Creating Updated test.py ===")
    
    try:
        # Read the current test.py file
        with open('test.py', 'r') as f:
            current_code = f.read()
        
        config = get_config_for_use_case('development')
        
        prompt = f"""
I need to create an updated Python Task class with these modifications:

1. Add timeToComplete parameter to Task constructor
2. Include timeToComplete in the to_dict method  
3. Update method descriptions

Please provide the complete updated Task class code with a timeToComplete field added. The class should have a constructor that takes title, description, done status, and timeToComplete parameters, and the to_dict method should include the timeToComplete field in the returned dictionary.
"""
        
        print("Creating updated test.py file...")
        
        # Try a simpler approach first
        try:
            async for message in query(prompt=prompt, options=config):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(f"{block.text}")
        except Exception as cli_error:
            print(f"CLI Error: {cli_error}")
            print("Trying alternative approach...")
            
            # Alternative: Use a simpler prompt
            simple_prompt = "Create Python Task class with timeToComplete parameter."
            
            try:
                async for message in query(prompt=simple_prompt, options=config):
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                print(f"{block.text}")
            except Exception as simple_error:
                print(f"Simple prompt also failed: {simple_error}")
                print("The CLI might need to be configured differently.")
                print("Try running: claude-code --help")
                        
    except FileNotFoundError:
        print("❌ test.py not found in current directory")
    except Exception as e:
        print(f"❌ Error creating updated file: {e}")


# async def check_prerequisites():
#     """Check if all prerequisites are met"""
#     print("=== Checking Prerequisites ===")
    
#     # Check if files exist
#     files_to_check = ['changes.json', 'test.py']
#     for file in files_to_check:
#         if os.path.exists(file):
#             print(f"✅ {file} found")
#         else:
#             print(f"❌ {file} not found")
#             return False
    
#     # Check if API key is set
#     if os.environ.get('ANTHROPIC_API_KEY'):
#         print("✅ ANTHROPIC_API_KEY is set")
#     else:
#         print("❌ ANTHROPIC_API_KEY not set")
#         print("Set it with: $env:ANTHROPIC_API_KEY = 'your-api-key'")
#         return False
    
#     print("✅ All prerequisites met!")
#     return True


import ast_chunker
import pyh_ast_generator

def regenerate_ast_files(py_file: str, repo_root: str = "."):
    py_path = Path(py_file).resolve()
    repo_root = Path(repo_root).resolve()
    out_root = repo_root / "out"

    rel_path = py_path.relative_to(repo_root)
    out_dir = out_root / rel_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    ast_json = out_dir / f"{py_path.stem}.ast.json"
    pyh_json = out_dir / f"{py_path.stem}.pyh.ast.json"

    print(f"\n🔄 Regenerating AST for {py_path}")

    try:
        chunker = ast_chunker.CodeChunker()
        result = chunker.chunk_file(str(py_path))
        ast_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"✅ Wrote {ast_json}")
    except Exception as e:
        print(f"❌ Chunker failed for {py_path}: {e}")
        return

    try:
        pyh_ast_generator.generate_pyh_with_claude(str(ast_json), str(pyh_json), str(py_path))
        print(f"✅ Wrote {pyh_json}")
    except Exception as e:
        print(f"❌ pyh generator failed for {py_path}: {e}")



async def main():
    print("Claude Code SDK - Apply Changes Demo")
    print("=" * 50)

    try:
        # Load the changes.json
        with open("changes.json", "r") as f:
            changes_data = json.load(f)

        # Option A: derive from ast_file
        ast_file = changes_data.get("ast_file", "")
        file_stem = Path(ast_file).stem.split(".")[0]  # "test01"

        # Option B (fallback): from metadata.source_file
        if not file_stem and "metadata" in changes_data:
            meta_source = changes_data["metadata"].get("source_file", "")
            file_stem = Path(meta_source).stem.split(".")[0]

        if not file_stem:
            raise ValueError("❌ Could not determine file stem from changes.json")

        # Call apply_changes and capture modified files
        modified_files = await apply_changes_from_json(file_stem)

        # If Claude actually modified files, regenerate AST/pyh
        if modified_files:
            print("\n🔄 Regenerating AST files for modified files...")
            for f in modified_files:
                regenerate_ast_files(f, repo_root=".")
        else:
            print("\n✅ No modified files returned, skipping AST regeneration")

        print("\n🎉 Demo completed successfully!")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

