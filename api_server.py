"""
FastAPI Server for HCLI Backend
Provides endpoints for crawling repositories, displaying pyh files, and converting pyh to py.
"""

import asyncio
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import existing modules
import crawl_repo
import pyh_ast_to_output
import diff_analyzer
import apply_changes_demo


app = FastAPI(
    title="HCLI Backend API",
    description="Backend API for HCLI - Human Code Language Interface",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class CrawlRequest(BaseModel):
    repo_path: str
    output_dir: Optional[str] = "out"


class CrawlResponse(BaseModel):
    success: bool
    message: str
    output_dir: str
    processed_files: List[str]


class DisplayPyhRequest(BaseModel):
    pyh_file_path: str


class DisplayPyhResponse(BaseModel):
    success: bool
    content: str
    file_path: str


class PyhToPyRequest(BaseModel):
    pyh_file_path: str
    original_pyh_content: str
    modified_pyh_content: str
    source_py_file: Optional[str] = None


class PyhToPyResponse(BaseModel):
    success: bool
    message: str
    changes_applied: bool
    modified_files: List[str]
    changes_json: Optional[Dict[str, Any]] = None


# Global storage for temporary files (in production, use a proper database)
temp_files: Dict[str, str] = {}


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "HCLI Backend API",
        "version": "1.0.0",
        "endpoints": {
            "crawl": "/crawl - Crawl a repository and generate pyh files",
            "display-pyh": "/display-pyh - Display pyh file content",
            "pyh-to-py": "/pyh-to-py - Convert pyh changes to py file updates"
        }
    }


@app.post("/crawl", response_model=CrawlResponse)
async def crawl_repository(request: CrawlRequest):
    """
    Crawl a repository and generate pyh AST files for all Python files.
    
    Args:
        request: Contains repo_path and optional output_dir
        
    Returns:
        CrawlResponse with success status and processed files list
    """
    try:
        repo_path = Path(request.repo_path)
        if not repo_path.exists():
            raise HTTPException(status_code=404, detail=f"Repository path not found: {repo_path}")
        
        output_dir = request.output_dir or "out"
        
        # Run the crawl_repo function
        crawl_repo.crawl_repo(str(repo_path), output_dir)
        
        # Find all generated pyh files
        output_path = repo_path / output_dir
        pyh_files = list(output_path.rglob("*.pyh.ast.json"))
        processed_files = [str(f.relative_to(repo_path)) for f in pyh_files]
        
        return CrawlResponse(
            success=True,
            message=f"Successfully crawled repository. Generated {len(processed_files)} pyh files.",
            output_dir=str(output_path),
            processed_files=processed_files
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawl failed: {str(e)}")


@app.post("/display-pyh", response_model=DisplayPyhResponse)
async def display_pyh_file(request: DisplayPyhRequest):
    """
    Display the content of a pyh file in a readable format.
    
    Args:
        request: Contains pyh_file_path
        
    Returns:
        DisplayPyhResponse with formatted content
    """
    try:
        pyh_path = Path(request.pyh_file_path)
        if not pyh_path.exists():
            raise HTTPException(status_code=404, detail=f"Pyh file not found: {pyh_path}")
        
        # Use the existing pyh_ast_to_output function to format the content
        content = pyh_ast_to_output.phy_ast_to_output(str(pyh_path))
        
        return DisplayPyhResponse(
            success=True,
            content=content,
            file_path=str(pyh_path)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to display pyh file: {str(e)}")


@app.post("/pyh-to-py", response_model=PyhToPyResponse)
async def convert_pyh_to_py(request: PyhToPyRequest):
    """
    Convert pyh changes to Python file updates.
    
    This endpoint:
    1. Creates temporary files for original and modified pyh content
    2. Runs diff_analyzer to generate changes.json
    3. Runs apply_changes_demo to apply changes to the Python file
    
    Args:
        request: Contains pyh file path, original content, modified content, and optional source py file
        
    Returns:
        PyhToPyResponse with success status and applied changes
    """
    try:
        # Generate unique session ID for temporary files
        session_id = str(uuid.uuid4())
        
        # Create temporary directory for this session
        temp_dir = Path(tempfile.mkdtemp(prefix=f"hcli_{session_id}_"))
        temp_files[session_id] = str(temp_dir)
        
        # Write original and modified pyh content to temporary files
        original_pyh_file = temp_dir / "original.pyh.ast.json"
        modified_pyh_file = temp_dir / "modified.pyh.ast.json"
        
        original_pyh_file.write_text(request.original_pyh_content, encoding="utf-8")
        modified_pyh_file.write_text(request.modified_pyh_content, encoding="utf-8")
        
        # Determine the source Python file
        source_py_file = request.source_py_file
        if not source_py_file:
            # Try to extract from pyh file metadata
            try:
                pyh_data = json.loads(request.original_pyh_content)
                metadata = pyh_data.get("metadata", {})
                source_py_file = metadata.get("source_file") or metadata.get("source_py")
                
                # Clean up the path if it's a .pyh.ast.json file
                if source_py_file and source_py_file.endswith(".pyh.ast.json"):
                    source_py_file = source_py_file.replace(".pyh.ast.json", ".py")
                    
            except json.JSONDecodeError:
                pass
        
        if not source_py_file:
            raise HTTPException(
                status_code=400, 
                detail="Source Python file not specified and could not be determined from pyh metadata"
            )
        
        # Check if source Python file exists
        source_py_path = Path(source_py_file)
        if not source_py_path.exists():
            raise HTTPException(status_code=404, detail=f"Source Python file not found: {source_py_path}")
        
        # Run diff_analyzer
        changes_json_file = temp_dir / "changes.json"
        
        # Create a DiffAnalyzer instance and run analysis
        analyzer = diff_analyzer.DiffAnalyzer(
            str(original_pyh_file),
            str(original_pyh_file),  # Using original as both files for now
            str(modified_pyh_file)
        )
        
        changes = analyzer.analyze_changes()
        changes_json = analyzer.to_json(changes)
        
        # Write changes.json
        changes_json_file.write_text(changes_json, encoding="utf-8")
        
        # Update the changes.json with correct source file path
        changes_data = json.loads(changes_json)
        changes_data["metadata"]["source_file"] = str(source_py_path)
        changes_json_file.write_text(json.dumps(changes_data, indent=2), encoding="utf-8")
        
        # Run apply_changes_demo
        try:
            # Change to temp directory to run apply_changes_demo
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            # Copy source file to temp directory
            temp_source_file = temp_dir / source_py_path.name
            temp_source_file.write_text(source_py_path.read_text(encoding="utf-8"), encoding="utf-8")
            
            # Run apply_changes_demo
            modified_files = await apply_changes_demo.apply_changes_from_json(source_py_path.stem)
            
            # Restore original working directory
            os.chdir(original_cwd)
            
            # Copy modified file back to original location if it was modified
            if modified_files and temp_source_file.exists():
                source_py_path.write_text(temp_source_file.read_text(encoding="utf-8"), encoding="utf-8")
            
            return PyhToPyResponse(
                success=True,
                message="Successfully converted pyh changes to Python file updates",
                changes_applied=True,
                modified_files=modified_files or [str(source_py_path)],
                changes_json=changes_data
            )
            
        except Exception as apply_error:
            return PyhToPyResponse(
                success=False,
                message=f"Changes analysis completed but application failed: {str(apply_error)}",
                changes_applied=False,
                modified_files=[],
                changes_json=changes_data
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pyh to py conversion failed: {str(e)}")
    
    finally:
        # Clean up temporary files
        if session_id in temp_files:
            temp_dir = Path(temp_files[session_id])
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)
            del temp_files[session_id]


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "HCLI Backend API is running"}


@app.get("/api/files")
async def get_files(directory: str = "test"):
    """Get directory contents for file explorer"""
    try:
        # Convert to absolute path
        base_path = Path.cwd()
        target_path = base_path / directory
        
        if not target_path.exists():
            raise HTTPException(status_code=404, detail=f"Directory {directory} not found")
        
        if not target_path.is_dir():
            raise HTTPException(status_code=400, detail=f"{directory} is not a directory")
        
        def build_file_tree(path: Path, relative_path: str = "") -> List[Dict[str, Any]]:
            """Recursively build file tree structure"""
            items = []
            
            try:
                for item in sorted(path.iterdir()):
                    item_relative_path = f"{relative_path}/{item.name}" if relative_path else item.name
                    
                    if item.is_dir():
                        # Skip hidden directories and common build/cache directories
                        if not item.name.startswith('.') and item.name not in ['__pycache__', 'node_modules', 'venv']:
                            children = build_file_tree(item, item_relative_path)
                            items.append({
                                "name": item.name,
                                "type": "folder",
                                "path": item_relative_path,
                                "children": children
                            })
                    else:
                        # Only include Python files and JSON files for now
                        if item.suffix in ['.py', '.json', '.pyh', '.txt']:
                            items.append({
                                "name": item.name,
                                "type": "file",
                                "path": item_relative_path
                            })
            except PermissionError:
                pass  # Skip directories we can't read
            
            return items
        
        file_tree = build_file_tree(target_path)
        return {"files": file_tree, "directory": directory}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading directory: {str(e)}")


@app.get("/api/file/{file_path:path}")
async def get_file_content(file_path: str):
    """Get the content of a specific file"""
    try:
        # Convert to absolute path
        base_path = Path.cwd()
        target_path = base_path / "test" / file_path
        
        if not target_path.exists():
            raise HTTPException(status_code=404, detail=f"File {file_path} not found")
        
        if not target_path.is_file():
            raise HTTPException(status_code=400, detail=f"{file_path} is not a file")
        
        # Read file content
        try:
            content = target_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # If it's a binary file, return a message
            content = f"[Binary file: {target_path.name}]"
        
        return {
            "file_path": file_path,
            "content": content,
            "size": target_path.stat().st_size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@app.get("/api/pyh-output/{file_path:path}")
async def get_pyh_output(file_path: str):
    """Get the pyh output for a specific file"""
    try:
        # Convert to absolute path
        base_path = Path.cwd()
        target_path = base_path / "test" / file_path
        
        if not target_path.exists():
            raise HTTPException(status_code=404, detail=f"File {file_path} not found")
        
        if not target_path.is_file():
            raise HTTPException(status_code=400, detail=f"{file_path} is not a file")
        
        # Check if it's a .py file
        if not target_path.suffix == '.py':
            raise HTTPException(status_code=400, detail=f"{file_path} is not a Python file")
        
        # Look for corresponding .ast.json file
        ast_file_path = target_path.with_suffix('.ast.json')
        if not ast_file_path.exists():
            # Try looking in out/ directory
            out_ast_file = base_path / "test" / "out" / ast_file_path.name
            if out_ast_file.exists():
                ast_file_path = out_ast_file
            else:
                raise HTTPException(status_code=404, detail=f"AST file for {file_path} not found")
        
        # Read and process the AST file
        try:
            with open(ast_file_path, 'r', encoding='utf-8') as f:
                ast_data = json.load(f)
            
            # Use the existing pyh_ast_to_output module to convert AST to readable format
            # First, let's use the render_node function to convert the AST data
            pyh_output_lines = []
            for node in ast_data.get("nodes", []):
                pyh_output_lines.extend(pyh_ast_to_output.render_node(node))
            pyh_output = "\n".join(pyh_output_lines)
            
            return {
                "file_path": file_path,
                "ast_file_path": str(ast_file_path.relative_to(base_path)),
                "pyh_output": pyh_output
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing AST file: {str(e)}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting pyh output: {str(e)}")


@app.get("/temp-files")
async def list_temp_files():
    """List active temporary file sessions (for debugging)"""
    return {"active_sessions": list(temp_files.keys())}


@app.delete("/temp-files/{session_id}")
async def cleanup_temp_files(session_id: str):
    """Clean up temporary files for a specific session"""
    if session_id not in temp_files:
        raise HTTPException(status_code=404, detail="Session not found")
    
    temp_dir = Path(temp_files[session_id])
    if temp_dir.exists():
        import shutil
        shutil.rmtree(temp_dir)
    
    del temp_files[session_id]
    return {"message": f"Cleaned up temporary files for session {session_id}"}


if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
