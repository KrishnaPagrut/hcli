from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from github_utils import clone_repo, list_files, get_file_content
import os

app = FastAPI()

# Allow frontend to call backend (important for React/Electron)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for hackathon demo, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/clone")
def clone_repo_endpoint(url: str = Query(...)):
    try:
        repo_path = clone_repo(url)
        repo_name = os.path.basename(repo_path)
        return {"repo": repo_name}
    except Exception as e:
        return {"error": str(e)}

@app.get("/files")
def list_repo_files(repo: str):
    return {"files": list(list_files(f"repos/{repo}"))}

@app.get("/file")
def get_file_content_endpoint(repo: str, path: str):
    return {"path": path, "content": get_file_content(f"repos/{repo}", path)}
