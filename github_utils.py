import os
import subprocess
import shutil


def clone_repo(repo_url: str, base_dir: str = "repos") -> str:
    """
    Clone a public GitHub repo into a local folder.
    Returns the path to the cloned repo.
    """
    os.makedirs(base_dir, exist_ok=True)

    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    repo_path = os.path.join(base_dir, repo_name)

    if os.path.exists(repo_path):
        print(f"[!] Repo already exists at {repo_path}")
    else:
        print(f"[+] Cloning {repo_url} into {repo_path}...")
        subprocess.run(["git", "clone", repo_url, repo_path], check=True)

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
    Yield all files in repo (optionally filter by extension).
    """
    for root, _, files in os.walk(repo_path):
        for file in files:
            if not extensions or file.endswith(tuple(extensions)):
                yield os.path.join(root, file)


def get_file_content(repo_path: str, file_path: str) -> str:
    """
    Read the contents of a file inside the repo.
    """
    full_path = os.path.join(repo_path, file_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()

# ------------------ Entry Point ------------------ #
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python github_utils.py <repo_url>")
    else:
        repo_url = sys.argv[1]
        repo_path = clone_repo(repo_url)
        cleanup_repo(repo_path)

        print("\nFiles in repo:")
        for f in list_files(repo_path, extensions=[".py"]):
            print("  ", f)