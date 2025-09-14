# crawl_repo.py
import os
import subprocess
from pathlib import Path

def crawl_repo(repo_root: str, out_root: str = "out"):
    repo_root = Path(repo_root).resolve()
    out_root = Path(out_root).resolve()

    for dirpath, _, filenames in os.walk(repo_root):
        for filename in filenames:
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

                # 1. Run AST chunker
                chunker_cmd = [
                    "python3", "ast_chunker.py",
                    str(py_file),
                    "-o", str(ast_json)
                ]
                result = subprocess.run(chunker_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Chunker failed for {py_file}:\n{result.stderr.strip()}")
                    continue
                print(f"Chunked → {ast_json}")

                # 2. Run pyh AST generator
                generator_cmd = [
                    "python3", "pyh_ast_generator.py",
                    str(ast_json),
                    "-o", str(pyh_json)
                ]
                result = subprocess.run(generator_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Generator failed for {py_file}:\n{result.stderr.strip()}")
                    continue
                print(f"Generated → {pyh_json}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root", help="Path to the root of the repo to crawl")
    parser.add_argument("-o", "--out", default="out", help="Output root directory (default: out)")
    args = parser.parse_args()

    crawl_repo(args.repo_root, args.out)
