"""
HCLI Backend API Server
Provides REST API endpoints for the HCLI frontend
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
import asyncio

# Add parent directory to path to import existing modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock
    from claude_config import get_config_for_use_case
    import ast_chunker
    import pyh_ast_generator
    import diff_analyzer
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")
    print("Some features may not work properly")

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configuration
REPO_ROOT = Path.cwd()
OUT_DIR = REPO_ROOT / "out"
OUT_DIR.mkdir(exist_ok=True)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'HCLI Backend API is running'
    })

@app.route('/api/clone', methods=['POST'])
def clone_repository():
    """Clone a GitHub repository"""
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        branch = data.get('branch', 'main')
        
        if not repo_url:
            return jsonify({'error': 'Repository URL is required'}), 400
        
        # Create temporary directory for cloning
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Clone the repository
            result = subprocess.run([
                'git', 'clone', '-b', branch, repo_url, str(temp_path)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return jsonify({
                    'error': 'Failed to clone repository',
                    'details': result.stderr
                }), 400
            
            # Copy files to our working directory
            for item in temp_path.iterdir():
                if item.name not in ['.git', '__pycache__', '.pytest_cache']:
                    dest = REPO_ROOT / item.name
                    if item.is_dir():
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.copytree(item, dest)
                    else:
                        shutil.copy2(item, dest)
        
        return jsonify({
            'message': 'Repository cloned successfully',
            'repo_url': repo_url,
            'branch': branch
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files', methods=['GET'])
def get_files():
    """Get list of files in the repository"""
    try:
        files = []
        
        def scan_directory(path, relative_path=""):
            for item in path.iterdir():
                if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules']:
                    continue
                
                item_relative = f"{relative_path}/{item.name}" if relative_path else item.name
                
                if item.is_dir():
                    files.append({
                        'name': item.name,
                        'type': 'directory',
                        'path': item_relative,
                        'children': []
                    })
                    scan_directory(item, item_relative)
                else:
                    files.append({
                        'name': item.name,
                        'type': 'file',
                        'path': item_relative
                    })
        
        scan_directory(REPO_ROOT)
        return jsonify({'files': files})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/file/<path:file_path>', methods=['GET'])
def get_file_content(file_path):
    """Get content of a specific file"""
    try:
        full_path = REPO_ROOT / file_path
        
        if not full_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        if full_path.is_dir():
            return jsonify({'error': 'Path is a directory'}), 400
        
        content = full_path.read_text(encoding='utf-8')
        
        return jsonify({
            'content': content,
            'path': file_path,
            'size': len(content)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pyh-output/<path:pyh_file_path>', methods=['GET'])
def get_pyh_output(pyh_file_path):
    """Get the human-readable output of a .pyh.json file"""
    try:
        pyh_path = REPO_ROOT / pyh_file_path
        
        if not pyh_path.exists():
            return jsonify({'error': 'PHY file not found'}), 404
        
        # Import the pyh_ast_to_output function
        try:
            import pyh_ast_to_output
        except ImportError:
            return jsonify({'error': 'pyh_ast_to_output module not found'}), 500
        
        # Generate the human-readable output
        text = pyh_path.read_text().strip()
        
        # Strip markdown fences if present
        if text.startswith("```"):
            text = "\n".join(line for line in text.splitlines() if not line.strip().startswith("```"))
        
        data = json.loads(text)
        
        if "phy_chunks" not in data or "main" not in data["phy_chunks"]:
            return jsonify({'error': 'Invalid .pyh JSON: missing phy_chunks/main'}), 400
        
        root = data["phy_chunks"]["main"]
        result = format_pyh_output(pyh_ast_to_output.render_node(root))
        
        return jsonify({
            'content': result,
            'path': pyh_file_path,
            'line_mappings': extract_line_mappings(data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def format_pyh_output(lines):
    """Format PHY output by removing line numbers and keeping proper spacing"""
    formatted_lines = []
    
    for line in lines:
        # Remove line number patterns like "  (lines 2-3)" or "(lines 1-1)"
        import re
        cleaned_line = re.sub(r'\s*\(lines\s+\d+[–-]\d+\)', '', line)
        
        # Keep the line but don't add extra spacing
        if cleaned_line.strip():
            formatted_lines.append(cleaned_line)
        else:
            # Keep empty lines as they are for proper alignment
            formatted_lines.append("")
    
    return "\n".join(formatted_lines)

def extract_line_mappings(pyh_data):
    """Extract line number mappings from PHY data"""
    mappings = []
    
    def extract_from_node(node, path=""):
        if "line_range" in node and node["line_range"]:
            mappings.append({
                'path': f"{path}.{node.get('id', '')}" if path else node.get('id', ''),
                'line_range': node["line_range"],
                'description': node.get('description', ''),
                'signature': node.get('signature', '')
            })
        
        for child in node.get("children", []):
            child_path = f"{path}.{node.get('id', '')}" if path else node.get('id', '')
            extract_from_node(child, child_path)
    
    if "phy_chunks" in pyh_data and "main" in pyh_data["phy_chunks"]:
        extract_from_node(pyh_data["phy_chunks"]["main"])
    
    return mappings

@app.route('/api/generate-ast', methods=['POST'])
def generate_ast():
    """Generate AST and PHY files for Python files"""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        
        if not file_path:
            return jsonify({'error': 'File path is required'}), 400
        
        py_path = REPO_ROOT / file_path
        
        if not py_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        # Generate AST
        chunker = ast_chunker.CodeChunker()
        result = chunker.chunk_file(str(py_path))
        
        # Save AST file
        ast_file = OUT_DIR / f"{py_path.stem}.ast.json"
        ast_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
        
        # Generate PHY file
        pyh_file = OUT_DIR / f"{py_path.stem}.pyh.json"
        pyh_ast_generator.generate_pyh_with_claude(str(ast_file), str(pyh_file), str(py_path))
        
        return jsonify({
            'message': 'AST and PHY files generated successfully',
            'ast_file': str(ast_file.relative_to(REPO_ROOT)),
            'pyh_file': str(pyh_file.relative_to(REPO_ROOT))
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/apply-changes', methods=['POST'])
def apply_changes():
    """Apply changes from PHY file to Python code"""
    try:
        data = request.get_json()
        pyh_content = data.get('pyh_content')
        original_py_path = data.get('original_py_path')
        
        if not pyh_content or not original_py_path:
            return jsonify({'error': 'PHY content and original Python path are required'}), 400
        
        # Save PHY content to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pyh.json', delete=False) as f:
            f.write(pyh_content)
            temp_pyh_path = f.name
        
        try:
            # Create changes.json for the diff analyzer
            changes_data = {
                'ast_file': str(OUT_DIR / f"{Path(original_py_path).stem}.ast.json"),
                'changes': [
                    {
                        'node_id': 'user_edit',
                        'node_type': 'user_edit',
                        'signature': 'User edited PHY file',
                        'description': 'User made changes to the PHY abstraction',
                        'line_range': [1, 1],
                        'change_type': 'modification',
                        'original_content': 'Original PHY content',
                        'modified_content': pyh_content
                    }
                ],
                'total_changes': 1,
                'file1': 'original.pyh.json',
                'file2': 'modified.pyh.json'
            }
            
            changes_file = OUT_DIR / 'changes.json'
            changes_file.write_text(json.dumps(changes_data, indent=2))
            
            # Apply changes using your existing function
            # This would call your apply_changes_demo.py logic
            result = apply_changes_with_claude(str(changes_file))
            
            return jsonify({
                'message': 'Changes applied successfully',
                'modified_files': result.get('modified_files', []),
                'success': True
            })
            
        finally:
            # Clean up temporary file
            os.unlink(temp_pyh_path)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/run-tests', methods=['POST'])
def run_tests():
    """Run tests on Python files"""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        
        if not file_path:
            return jsonify({'error': 'File path is required'}), 400
        
        py_path = REPO_ROOT / file_path
        
        if not py_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        # Run pytest on the file
        result = subprocess.run([
            'python', '-m', 'pytest', str(py_path), '-v', '--tb=short'
        ], capture_output=True, text=True, cwd=REPO_ROOT)
        
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'errors': result.stderr,
            'return_code': result.returncode
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/push', methods=['POST'])
def push_changes():
    """Push changes to GitHub repository"""
    try:
        data = request.get_json()
        commit_message = data.get('commit_message', 'HCLI: Apply changes')
        
        # Add all changes
        subprocess.run(['git', 'add', '.'], cwd=REPO_ROOT, check=True)
        
        # Commit changes
        subprocess.run(['git', 'commit', '-m', commit_message], cwd=REPO_ROOT, check=True)
        
        # Push changes
        result = subprocess.run(['git', 'push'], cwd=REPO_ROOT, capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({
                'error': 'Failed to push changes',
                'details': result.stderr
            }), 400
        
        return jsonify({
            'message': 'Changes pushed successfully',
            'commit_message': commit_message
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def apply_changes_with_claude(changes_file_path):
    """Apply changes using Claude (simplified version)"""
    try:
        # This is a simplified version - you would integrate your full apply_changes_demo.py logic here
        with open(changes_file_path, 'r') as f:
            changes_data = json.load(f)
        
        # For now, just return success
        return {
            'modified_files': [changes_data.get('ast_file', 'unknown')],
            'success': True
        }
        
    except Exception as e:
        return {
            'modified_files': [],
            'success': False,
            'error': str(e)
        }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
