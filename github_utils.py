import os
import subprocess
import shutil


def clone_repo(repo_url: str, base_dir: str = "repos", force: bool = False) -> str:
    """
    Clone a public GitHub repo into a local folder.
    Cleans up unnecessary files after cloning.
    Returns the path to the cloned repo.

    Args:
        repo_url: GitHub repo URL
        base_dir: base directory where repos are stored
        force: if True, delete repo if it already exists and re-clone
    """
    os.makedirs(base_dir, exist_ok=True)

    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    repo_path = os.path.join(base_dir, repo_name)

    if os.path.exists(repo_path):
        if force:
            print(f"[!] Removing existing repo at {repo_path} (force=True)")
            shutil.rmtree(repo_path)
        else:
            print(f"[!] Repo already exists at {repo_path}, skipping clone")
            return repo_path

    print(f"[+] Cloning {repo_url} into {repo_path}...")
    subprocess.run(["git", "clone", repo_url, repo_path], check=True)
    cleanup_repo(repo_path)  # auto-cleanup right after cloning

    return repo_path


def cleanup_repo(repo_path: str):
    """
    Remove unnecessary folders like .git, node_modules, __pycache__.
    Keeps repo lightweight for parsing.
    """
    for folder in [".git", "node_modules", "__pycache__"]:
        target = os.path.join(repo_path, folder)
        if os.path.exists(target):
            try:
                shutil.rmtree(target)
                print(f"[+] Removed {target}")
            except PermissionError:
                print(f"[!] Skipped {target} (permission error)")


def list_files(repo_path: str, extensions=None):
    """
    Yield all file paths in repo (relative to repo root).
    Normalizes paths to forward slashes for frontend compatibility.
    """
    for root, _, files in os.walk(repo_path):
        for file in files:
            if not extensions or file.endswith(tuple(extensions)):
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, repo_path)
                yield rel_path.replace("\\", "/")  # ✅ normalize here


def get_file_content(repo_path: str, file_path: str) -> str:
    """
    Read the contents of a file inside the repo.
    """
    full_path = os.path.join(repo_path, file_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    print(f"[📂] Reading file: {file_path}")  # helpful debug log
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


# ------------------ Entry Point ------------------ #
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python github_utils.py <repo_url> [--force]")
    else:
        repo_url = sys.argv[1]
        force_flag = "--force" in sys.argv
        repo_path = clone_repo(repo_url, force=force_flag)

        print("\nFiles in repo:")
        for f in list_files(repo_path, extensions=[".py"]):
            print("  ", f)
    