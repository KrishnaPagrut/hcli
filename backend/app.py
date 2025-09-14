"""
HCLI IDE Backend API
Provides REST API endpoints for the HCLI IDE frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
import re
import sys

# Add the parent directory to the path so we can import pyh_ast_to_output and github_utils
sys.path.append(str(Path(__file__).parent.parent))
import pyh_ast_to_output
import github_utils

try:
    import ast_chunker
    import pyh_ast_generator
    import pyh_ast_to_output
    import diff_analyzer
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")
    print("Some features may not work properly")

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configuration
REPO_ROOT = Path(__file__).parent.parent  # Go up one level from backend to hcli root
OUT_DIR = REPO_ROOT / "out"
OUT_DIR.mkdir(exist_ok=True)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'HCLI IDE Backend API is running'
    })

@app.route('/api/clone-repo', methods=['POST'])
def clone_repo():
    """Clone a GitHub repository (without crawling)"""
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        force = data.get('force', False)
        
        if not repo_url:
            return jsonify({'error': 'repo_url is required'}), 400
        
        # Clone the repository
        repo_path = github_utils.clone_repo(repo_url, force=force)
        
        # Get list of files in the repository
        files = list(github_utils.list_files(repo_path, extensions=['.py']))
        
        return jsonify({
            'message': 'Repository cloned successfully',
            'repo_path': repo_path,
            'repo_name': Path(repo_path).name,
            'files': files
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/repo-files', methods=['GET'])
def get_repo_files():
    """Get files from a cloned repository"""
    try:
        repo_path = request.args.get('repo_path')
        
        if not repo_path:
            return jsonify({'error': 'repo_path is required'}), 400
        
        if not os.path.exists(repo_path):
            return jsonify({'error': 'Repository path does not exist'}), 404
        
        files = list(github_utils.list_files(repo_path, extensions=['.py']))
        
        return jsonify({
            'files': files,
            'repo_path': repo_path,
            'repo_name': Path(repo_path).name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/api/crawl-repo', methods=['POST'])
def crawl_repository():
    """Crawl repository and generate AST files for all Python files"""
    try:
        data = request.get_json()
        repo_path = data.get('repo_path', '/Users/krishnapagrut/Developer/hcli_test')  # Default to hcli_test
        
        # Run crawl_repo.py from the hcli directory but target the specified directory
        hcli_dir = Path(__file__).parent.parent  # Go back to hcli root
        result = subprocess.run([
            'python3', 'crawl_repo.py', repo_path, '-o', 'out'
        ], cwd=hcli_dir, capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({
                'error': 'Failed to crawl repository',
                'details': result.stderr
            }), 400
        
        return jsonify({
            'message': 'Repository crawled successfully',
            'output': result.stdout,
            'repo_path': repo_path
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files', methods=['GET'])
def get_files():
    """Get list of files in the repository"""
    try:
        # Get directory from query parameter, default to REPO_ROOT
        directory = request.args.get('directory', str(REPO_ROOT))
        target_dir = Path(directory)
        
        if not target_dir.exists():
            return jsonify({'error': 'Directory not found'}), 404
        
        files = []
        
        def scan_directory(path, relative_path=""):
            current_files = []
            print(f"Scanning directory: {path} (relative: {relative_path})")
            
            try:
                for item in path.iterdir():
                    print(f"  Found item: {item.name} (is_dir: {item.is_dir()})")
                    
                    if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules', 'out']:
                        print(f"    Skipping {item.name} (filtered)")
                        continue
                    
                    item_relative = f"{relative_path}/{item.name}" if relative_path else item.name
                    
                    if item.is_dir():
                        print(f"    Processing directory: {item.name}")
                        children = scan_directory(item, item_relative)
                        current_files.append({
                            'name': item.name,
                            'type': 'directory',
                            'path': item_relative,
                            'children': children
                        })
                        print(f"    Added directory {item.name} with {len(children)} children")
                    else:
                        print(f"    Processing file: {item.name}")
                        current_files.append({
                            'name': item.name,
                            'type': 'file',
                            'path': item_relative
                        })
                        print(f"    Added file {item.name}")
            except PermissionError as e:
                print(f"    Permission error accessing {path}: {e}")
            except Exception as e:
                print(f"    Error scanning {path}: {e}")
                
            print(f"  Returning {len(current_files)} items from {path}")
            return current_files
        
        files = scan_directory(target_dir)
        print(f"Scanned directory {target_dir}, found {len(files)} items")
        for item in files:
            print(f"  - {item['name']} ({item['type']})")
            if item['type'] == 'directory' and item['children']:
                print(f"    Children: {len(item['children'])}")
        return jsonify({'files': files, 'directory': str(target_dir)})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/file/<path:file_path>', methods=['GET'])
def get_file_content(file_path):
    """Get content of a specific file"""
    try:
        # Get directory from query parameter, default to REPO_ROOT
        directory = request.args.get('directory', str(REPO_ROOT))
        target_dir = Path(directory)
        full_path = target_dir / file_path
        
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

@app.route('/api/pyh-output/<path:py_file_path>', methods=['GET'])
def get_pyh_output(py_file_path):
    """Get the human-readable output of a .py file by finding its corresponding .ast.pyh.json file"""
    try:
        # Get directory from query parameter, default to REPO_ROOT
        directory = request.args.get('directory', str(REPO_ROOT))
        target_dir = Path(directory)
        py_path = target_dir / py_file_path
        
        if not py_path.exists():
            return jsonify({'error': 'Python file not found'}), 404
        
        # Look for corresponding .ast.pyh.json file in the out directory
        # For files in subdirectories, maintain the same subdirectory structure in out/
        out_dir = target_dir / "out"
        
        # Get the relative path from the target directory
        relative_path = py_path.relative_to(target_dir)
        
        # If the file is in a subdirectory, create the same structure in out/
        if len(relative_path.parts) > 1:
            # File is in a subdirectory
            subdir = relative_path.parent
            pyh_path = out_dir / subdir / f"{py_path.stem}.pyh.ast.json"
        else:
            # File is in the root directory
            pyh_path = out_dir / f"{py_path.stem}.pyh.ast.json"
        
        if not pyh_path.exists():
            return jsonify({'error': 'No corresponding .ast.pyh.json file found'}), 404
        
        # Check if user PHY content exists first
        # Use the same subdirectory structure for user files
        if len(relative_path.parts) > 1:
            # File is in a subdirectory
            subdir = relative_path.parent
            user_file_path = out_dir / subdir / f"{py_path.stem}.pyh.user.txt"
        else:
            # File is in the root directory
            user_file_path = out_dir / f"{py_path.stem}.pyh.user.txt"
        
        if user_file_path.exists():
            # Return user's edited PHY content
            result = user_file_path.read_text(encoding='utf-8')
            return jsonify({
                'content': result,
                'path': py_file_path,
                'is_user_edited': True,
                'line_mappings': []  # No line mappings for user content
            })
        
        # Generate the human-readable output from AST
        text = pyh_path.read_text().strip()
        
        # Strip markdown fences if present
        if text.startswith("```"):
            text = "\n".join(line for line in text.splitlines() if not line.strip().startswith("```"))
        
        data = json.loads(text)
        
        if "phy_chunks" not in data or "main" not in data["phy_chunks"]:
            return jsonify({'error': 'Invalid .pyh JSON: missing phy_chunks/main'}), 400
        
        root = data["phy_chunks"]["main"]
        
        result = format_pyh_output(pyh_ast_to_output.render_node(root))
        
        # Save strict version (original PHY output) to out/.pyh.strict.txt
        # Create subdirectory if needed
        if len(relative_path.parts) > 1:
            subdir = relative_path.parent
            (out_dir / subdir).mkdir(parents=True, exist_ok=True)
            strict_file_path = out_dir / subdir / f"{py_path.stem}.pyh.strict.txt"
        else:
            out_dir.mkdir(exist_ok=True)
            strict_file_path = out_dir / f"{py_path.stem}.pyh.strict.txt"
        strict_file_path.write_text(result, encoding='utf-8')
        
        return jsonify({
            'content': result,
            'path': py_file_path,
            'is_user_edited': False,
            'line_mappings': extract_line_mappings(data),
            'strict_file_path': str(strict_file_path.relative_to(target_dir)),
            'phy_data': data  # Include the PHY AST data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def format_pyh_output(lines):
    """Format PHY output by removing line numbers and keeping proper spacing"""
    formatted_lines = []
    
    for line in lines:
        # Remove line number patterns like "  (lines 2-3)" or "(lines 1-1)"
        cleaned_line = re.sub(r'\s*\(lines\s+\d+[–-]\d+\)', '', line)
        
        # Keep the line but don't add extra spacing
        if cleaned_line.strip():
            formatted_lines.append(cleaned_line)
        else:
            # Keep empty lines as they are for proper alignment
            formatted_lines.append("")
    
    return "\n".join(formatted_lines)

def extract_line_mappings(pyh_data):
    """Extract line number mappings from PHY data with proper chunk-to-chunk mapping"""
    mappings = []
    pyh_line_counter = [0]  # Use list to allow modification in nested function
    
    def extract_from_node(node, path=""):
        if "line_range" in node and node["line_range"]:
            # Map PHY lines to Python lines based on the actual line ranges
            py_start, py_end = node["line_range"]
            
            # For each line in the PHY content that corresponds to this node
            # We need to map it to the appropriate Python line range
            pyh_start = pyh_line_counter[0] + 1
            
            # Count how many lines this node will generate in PHY content
            phy_lines_for_node = 0
            if node.get('signature'):
                phy_lines_for_node += 1
            if node.get('description'):
                phy_lines_for_node += 1
            
            # If no signature or description, count as 1 line
            if phy_lines_for_node == 0:
                phy_lines_for_node = 1
            
            pyh_end = pyh_start + phy_lines_for_node - 1
            
            # Create mapping for each PHY line to Python line range
            for i in range(phy_lines_for_node):
                pyh_line = pyh_start + i
                # Map to the corresponding Python line (distribute across the range)
                if py_end > py_start:
                    py_line = py_start + int((i / max(1, phy_lines_for_node - 1)) * (py_end - py_start))
                else:
                    py_line = py_start
                
                mappings.append({
                    'pyhLine': pyh_line,
                    'pyLine': py_line,
                    'description': node.get('description', ''),
                    'signature': node.get('signature', ''),
                    'nodeId': node.get('id', ''),
                    'nodeType': node.get('type', ''),
                    'pyLineRange': [py_start, py_end]
                })
            
            pyh_line_counter[0] += phy_lines_for_node
        
        # Process children
        for child in node.get("children", []):
            child_path = f"{path}.{node.get('id', '')}" if path else node.get('id', '')
            extract_from_node(child, child_path)
    
    if "phy_chunks" in pyh_data and "main" in pyh_data["phy_chunks"]:
        extract_from_node(pyh_data["phy_chunks"]["main"])
    
    return mappings

@app.route('/api/apply-changes', methods=['POST'])
def apply_changes():
    """Apply changes from PHY file to Python code"""
    try:
        data = request.get_json()
        pyh_content = data.get('pyh_content')
        original_py_path = data.get('original_py_path')
        diffs = data.get('diffs', [])
        
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
                        'node_id': f'user_edit_{i}',
                        'node_type': 'user_edit',
                        'signature': diff.get('description', 'User edit'),
                        'description': diff.get('description', 'User made changes'),
                        'line_range': diff.get('lineRange', [1, 1]),
                        'change_type': diff.get('type', 'modification'),
                        'original_content': diff.get('originalContent', ''),
                        'modified_content': diff.get('modifiedContent', '')
                    }
                    for i, diff in enumerate(diffs)
                ],
                'total_changes': len(diffs),
                'file1': 'original.pyh.json',
                'file2': 'modified.pyh.json'
            }
            
            changes_file = OUT_DIR / 'changes.json'
            changes_file.write_text(json.dumps(changes_data, indent=2))
            
            # Apply changes using your existing function
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

@app.route('/api/save-user-phy', methods=['POST'])
def save_user_phy():
    """Save user-edited PHY content as .pyh.user.txt"""
    try:
        data = request.get_json()
        py_file_path = data.get('py_file_path')
        phy_content = data.get('phy_content')
        
        if not py_file_path or not phy_content:
            return jsonify({'error': 'Python file path and PHY content are required'}), 400
        
        # Get directory from query parameter, default to REPO_ROOT
        directory = request.args.get('directory', str(REPO_ROOT))
        target_dir = Path(directory)
        py_path = target_dir / py_file_path
        
        if not py_path.exists():
            return jsonify({'error': 'Python file not found'}), 404
        
        # Save user version to out/.pyh.user.txt
        out_dir = target_dir / "out"
        out_dir.mkdir(exist_ok=True)
        user_file_path = out_dir / f"{py_path.stem}.pyh.user.txt"
        user_file_path.write_text(phy_content, encoding='utf-8')
        
        return jsonify({
            'message': 'User PHY content saved successfully',
            'user_file_path': str(user_file_path.relative_to(target_dir))
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/apply-phy-changes', methods=['POST'])
def apply_phy_changes():
    """Apply changes using diff_analyzer and apply_changes_demo"""
    try:
        data = request.get_json()
        py_file_path = data.get('py_file_path')
        
        if not py_file_path:
            return jsonify({'error': 'Python file path is required'}), 400
        
        # Get directory from query parameter, default to REPO_ROOT
        directory = request.args.get('directory', str(REPO_ROOT))
        target_dir = Path(directory)
        py_path = target_dir / py_file_path
        
        if not py_path.exists():
            return jsonify({'error': 'Python file not found'}), 404
        
        # Find the corresponding files
        out_dir = target_dir / "out"
        
        # Get the relative path from the target directory
        relative_path = py_path.relative_to(target_dir)
        
        # Use the same subdirectory structure for all files
        if len(relative_path.parts) > 1:
            # File is in a subdirectory
            subdir = relative_path.parent
            strict_file_path = out_dir / subdir / f"{py_path.stem}.pyh.strict.txt"
            user_file_path = out_dir / subdir / f"{py_path.stem}.pyh.user.txt"
            pyh_json_path = out_dir / subdir / f"{py_path.stem}.pyh.ast.json"
        else:
            # File is in the root directory
            strict_file_path = out_dir / f"{py_path.stem}.pyh.strict.txt"
            user_file_path = out_dir / f"{py_path.stem}.pyh.user.txt"
            pyh_json_path = out_dir / f"{py_path.stem}.pyh.ast.json"
        
        if not strict_file_path.exists():
            return jsonify({'error': 'Strict PHY file not found. Please load the file first.'}), 404
        
        if not user_file_path.exists():
            return jsonify({'error': 'User PHY file not found. Please save your edits first.'}), 404
        
        if not pyh_json_path.exists():
            return jsonify({'error': 'PHY JSON file not found. Please crawl the directory first.'}), 404
        
        # Create temporary copy of original file
        temp_original_path = out_dir / f"{py_path.stem}.temp_original.py"
        import shutil
        shutil.copy2(py_path, temp_original_path)
        
        try:
            # Run diff_analyzer.py from the hcli directory
            hcli_dir = Path(__file__).parent.parent  # Go back to hcli root
            changes_file = target_dir / "changes.json"
            diff_result = subprocess.run([
                'python3', 'diff_analyzer.py', 
                str(pyh_json_path), str(strict_file_path), str(user_file_path), 
                '-o', str(changes_file)
            ], cwd=hcli_dir, capture_output=True, text=True)
            
            if diff_result.returncode != 0:
                return jsonify({
                    'error': 'Failed to analyze diff',
                    'details': diff_result.stderr
                }), 400
            
            # Run apply_changes_demo.py from the target directory (where changes.json is located)
            apply_result = subprocess.run([
                'python3', str(hcli_dir / 'apply_changes_demo.py'), str(py_path)
            ], cwd=target_dir, capture_output=True, text=True)
            
            if apply_result.returncode != 0:
                return jsonify({
                    'error': 'Failed to apply changes',
                    'details': apply_result.stderr
                }), 400
            
            # Compare files to detect changes
            files_changed = []
            if temp_original_path.exists() and py_path.exists():
                with open(temp_original_path, 'r') as f1, open(py_path, 'r') as f2:
                    original_content = f1.read()
                    new_content = f2.read()
                    
                    if original_content != new_content:
                        files_changed.append(str(py_path))
                        print(f"File {py_path} was modified, will regenerate AST/PHY")
                    else:
                        print(f"File {py_path} was not modified, skipping AST/PHY regeneration")
            
            # Regenerate AST and PHY files if changes were detected
            if files_changed:
                print(f"Regenerating AST/PHY for {len(files_changed)} modified files...")
                for file_path in files_changed:
                    file_stem = Path(file_path).stem
                    # Regenerate AST
                    ast_result = subprocess.run([
                        'python3', 'pyh_ast_generator.py', file_path
                    ], cwd=target_dir, capture_output=True, text=True)
                    
                    if ast_result.returncode == 0:
                        print(f"Regenerated AST for {file_stem}")
                    else:
                        print(f"Failed to regenerate AST for {file_stem}: {ast_result.stderr}")
                    
                    # Regenerate PHY
                    phy_result = subprocess.run([
                        'python3', 'pyh_ast_to_output.py', f"{file_stem}.ast.json"
                    ], cwd=target_dir, capture_output=True, text=True)
                    
                    if phy_result.returncode == 0:
                        print(f"Regenerated PHY for {file_stem}")
                    else:
                        print(f"Failed to regenerate PHY for {file_stem}: {phy_result.stderr}")
            
            # Clean up temporary files and user PHY file before returning
            if temp_original_path.exists():
                temp_original_path.unlink()
                print(f"Cleaned up temporary file: {temp_original_path}")
            
            if user_file_path.exists():
                user_file_path.unlink()
                print(f"Cleaned up user PHY file: {user_file_path}")
            
            return jsonify({
                'message': 'Changes applied successfully',
                'py_file_path': py_file_path,
                'diff_output': diff_result.stdout,
                'apply_output': apply_result.stdout,
                'files_changed': files_changed,
                'regenerated_files': files_changed
            })
            
        finally:
            # Ensure cleanup even if an exception occurs
            if temp_original_path.exists():
                temp_original_path.unlink()
                print(f"Cleaned up temporary file (finally): {temp_original_path}")
            
            if user_file_path.exists():
                user_file_path.unlink()
                print(f"Cleaned up user PHY file (finally): {user_file_path}")
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
