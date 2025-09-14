# crawl_repo.py
import os
from pathlib import Path
import ast_chunker
import pyh_ast_generator

# Directories and file patterns to ignore
IGNORE_DIRS = {
    ".git", ".github", ".gitlab", ".idea", ".vscode",
    "venv", ".venv", "env", ".env",
    "__pycache__", "build", "dist"
}
IGNORE_SUFFIXES = {".egg-info", ".pyc", ".pyo"}

def crawl_repo(repo_root: str, out_root: str = "out"):
    repo_root = Path(repo_root).resolve()
    out_root = repo_root / "out"

    for dirpath, dirnames, filenames in os.walk(repo_root):
        # Filter out ignored directories in-place
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for filename in filenames:
            # Skip unwanted suffixes
            if any(filename.endswith(suffix) for suffix in IGNORE_SUFFIXES):
                continue

            if filename.endswith(".py"):
                py_file = Path(dirpath) / filename

                # Skip files inside the out directory itself
                if out_root in py_file.parents:
                    continue

                # Mirror the folder structure into out/
                rel_path = py_file.relative_to(repo_root)
                out_dir = out_root / rel_path.parent
                out_dir.mkdir(parents=True, exist_ok=True)

                # Output file paths
                ast_json = out_dir / f"{py_file.stem}.ast.json"
                pyh_json = out_dir / f"{py_file.stem}.pyh.json"

                print(f"\n📄 Processing {py_file}")

                # 1. Run AST chunker (imported directly)
                try:
                    chunker = ast_chunker.CodeChunker()
                    result = chunker.chunk_file(str(py_file))
                    ast_json.write_text(
                        __import__("json").dumps(result, indent=2),
                        encoding="utf-8"
                    )
                    print(f"✅ Chunked → {ast_json}")
                except Exception as e:
                    print(f"❌ Chunker failed for {py_file}: {e}")
                    continue

                # 2. Run pyh AST generator (imported directly)
                try:
                    pyh_ast_generator.generate_pyh_with_claude(
                        str(ast_json), str(pyh_json), str(py_file)
                    )
                    print(f"✅ Generated → {pyh_json}")
                except Exception as e:
                    print(f"❌ Generator failed for {py_file}: {e}")
                    continue


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root", help="Path to the root of the repo to crawl")
    parser.add_argument("-o", "--out", default="out", help="Output root directory (default: out)")
    args = parser.parse_args()

    crawl_repo(args.repo_root, args.out)
