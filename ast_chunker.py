import ast
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class CodeChunker:
    def __init__(self):
        self.chunks = {}
        self.chunk_counters = {
            'if': 0, 'elif': 0, 'else': 0, 'for': 0, 'while': 0,
            'try': 0, 'except': 0, 'finally': 0, 'with': 0,
            'function': 0, 'class': 0, 'method': 0
        }
        self.source_lines = []
        self.node_to_chunk_id = {}  # Maps AST nodes to their chunk IDs
        self.if_node_to_chunk_id = {}  # Maps individual if/elif/else nodes to their chunk IDs
        self.else_chunk_to_statements = {}  # Maps else chunk IDs to their statement lists
        
    def chunk_file(self, file_path: str) -> Dict[str, Any]:
        """Main entry point to chunk a Python file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        self.source_lines = source_code.split('\n')
        
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            return self._create_error_chunk(source_code, str(e))
        
        # PASS 1: Create all chunk IDs and basic structure
        self._first_pass_create_ids(tree)
        
        # PASS 2: Populate code_blocks with actual content and references
        self._second_pass_populate_content(tree)
        
        return self._create_output_structure(file_path)
    
    def _first_pass_create_ids(self, tree: ast.AST):
        """First pass: Create all chunk IDs and basic structure"""
        
        # Create main chunk
        self.chunks["main"] = {
            "id": "main",
            "type": "module", 
            "code_blocks": [],  # Will be populated in second pass
            # "dependencies": [],
            # "defines": self._extract_top_level_definitions(tree),
            "parent_scope": None
        }
        
        # Process all nodes to create chunk IDs
        self._create_ids_recursive(tree.body, "main")
    
    def _create_ids_recursive(self, nodes: List[ast.AST], parent_scope: str):
        """Recursively create IDs for all nodes that need chunks"""
        
        for node in nodes:
            # Class definitions
            if isinstance(node, ast.ClassDef):
                chunk_id = f"class_{node.name}"
                self.chunks[chunk_id] = {
                    "id": chunk_id,
                    "type": "class_definition",
                    "code_blocks": [],
                    # "dependencies": [],
                    # "defines": [node.name],
                    "parent_scope": parent_scope
                }
                self.node_to_chunk_id[node] = chunk_id
                
                # Process class methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_id = f"{node.name}_{item.name}"
                        self.chunks[method_id] = {
                            "id": method_id,
                            "type": "method_definition",
                            "code_blocks": [],
                            # "dependencies": [],
                            # "defines": [],
                            "parent_scope": chunk_id
                        }
                        self.node_to_chunk_id[item] = method_id
                        
                        # Process method body
                        self._create_ids_recursive(item.body, method_id)
            
            # Function definitions
            elif isinstance(node, ast.FunctionDef):
                self.chunk_counters['function'] += 1
                chunk_id = f"function_{node.name}"
                self.chunks[chunk_id] = {
                    "id": chunk_id,
                    "type": "function_definition",
                    "code_blocks": [],
                    # "dependencies": [],
                    # "defines": [node.name],
                    "parent_scope": parent_scope
                }
                self.node_to_chunk_id[node] = chunk_id
                
                # Process function body
                self._create_ids_recursive(node.body, chunk_id)
            
            # If statements
            elif isinstance(node, ast.If):
                self.chunk_counters['if'] += 1
                container_id = f"if{self.chunk_counters['if']}_block"
                
                # Container chunk for the entire if/elif/else structure
                self.chunks[container_id] = {
                    "id": container_id,
                    "type": "if_else_block",
                    "code_blocks": [],
                    # "dependencies": [],
                    # "defines": [],
                    "parent_scope": parent_scope
                }
                self.node_to_chunk_id[node] = container_id
                
                # Individual if chunk
                if_id = f"if{self.chunk_counters['if']}"
                self.chunks[if_id] = {
                    "id": if_id,
                    "type": "if_statement", 
                    "code_blocks": [],
                    # "dependencies": [],
                    # "defines": [],
                    "parent_scope": container_id
                }
                # Map the individual if node to its chunk ID
                self.if_node_to_chunk_id[node] = if_id
                
                # Process if body
                self._create_ids_recursive(node.body, if_id)
                
                # Handle elif/else chains
                current = node
                while current.orelse:
                    if len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
                        # This is an elif
                        self.chunk_counters['elif'] += 1
                        elif_node = current.orelse[0]
                        elif_id = f"elif{self.chunk_counters['elif']}"
                        
                        self.chunks[elif_id] = {
                            "id": elif_id,
                            "type": "elif_statement",
                            "code_blocks": [],
                            # "dependencies": [],
                            # "defines": [],
                            "parent_scope": container_id
                        }
                        # Map the elif node to its chunk ID
                        self.if_node_to_chunk_id[elif_node] = elif_id
                        
                        self._create_ids_recursive(elif_node.body, elif_id)
                        current = elif_node
                    else:
                        # This is an else
                        self.chunk_counters['else'] += 1
                        else_id = f"else{self.chunk_counters['else']}"
                        
                        self.chunks[else_id] = {
                            "id": else_id,
                            "type": "else_statement",
                            "code_blocks": [],
                            # "dependencies": [],
                            # "defines": [],
                            "parent_scope": container_id
                        }
                        # Map the else statements to their chunk ID
                        # Note: else is a list of statements, not a single node
                        self.else_chunk_to_statements[else_id] = current.orelse
                        
                        self._create_ids_recursive(current.orelse, else_id)
                        break
            
            # For loops
            elif isinstance(node, ast.For):
                self.chunk_counters['for'] += 1
                chunk_id = f"for{self.chunk_counters['for']}_loop"
                
                self.chunks[chunk_id] = {
                    "id": chunk_id,
                    "type": "for_loop",
                    "code_blocks": [],
                    # "dependencies": [],
                    # "defines": [node.target.id if isinstance(node.target, ast.Name) else "loop_var"],
                    "parent_scope": parent_scope
                }
                self.node_to_chunk_id[node] = chunk_id
                
                # Process for body
                self._create_ids_recursive(node.body, chunk_id)
            
            # While loops  
            elif isinstance(node, ast.While):
                self.chunk_counters['while'] += 1
                chunk_id = f"while{self.chunk_counters['while']}_loop"
                
                self.chunks[chunk_id] = {
                    "id": chunk_id,
                    "type": "while_loop",
                    "code_blocks": [],
                    # "dependencies": [],
                    # "defines": [],
                    "parent_scope": parent_scope
                }
                self.node_to_chunk_id[node] = chunk_id
                
                # Process while body
                self._create_ids_recursive(node.body, chunk_id)
            
            # Try statements
            elif isinstance(node, ast.Try):
                self.chunk_counters['try'] += 1
                chunk_id = f"try{self.chunk_counters['try']}_block"
                
                self.chunks[chunk_id] = {
                    "id": chunk_id,
                    "type": "try_statement",
                    "code_blocks": [],
                    # "dependencies": [],
                    # "defines": [],
                    "parent_scope": parent_scope
                }
                self.node_to_chunk_id[node] = chunk_id
                
                # Process try body and handlers
                self._create_ids_recursive(node.body, chunk_id)
                for handler in node.handlers:
                    self._create_ids_recursive(handler.body, chunk_id)
                if node.orelse:
                    self._create_ids_recursive(node.orelse, chunk_id)
                if node.finalbody:
                    self._create_ids_recursive(node.finalbody, chunk_id)
            
            # With statements
            elif isinstance(node, ast.With):
                self.chunk_counters['with'] += 1
                chunk_id = f"with{self.chunk_counters['with']}_statement"
                
                self.chunks[chunk_id] = {
                    "id": chunk_id,
                    "type": "with_statement",
                    "code_blocks": [],
                    # "dependencies": [],
                    # "defines": [],
                    "parent_scope": parent_scope
                }
                self.node_to_chunk_id[node] = chunk_id
                
                # Process with body
                self._create_ids_recursive(node.body, chunk_id)
            
            # For other nodes, continue recursively if they have body
            elif hasattr(node, 'body') and isinstance(node.body, list):
                self._create_ids_recursive(node.body, parent_scope)
    
    def _second_pass_populate_content(self, tree: ast.AST):
        """Second pass: Populate code_blocks with actual content"""
        
        # Populate main chunk - only references to top-level items
        main_blocks = []
        for node in tree.body:
            if node in self.node_to_chunk_id:
                # This node has its own chunk
                main_blocks.append({
                    "type": "chunk_ref",
                    "chunk_id": self.node_to_chunk_id[node],
                    "line_range": [node.lineno, getattr(node, 'end_lineno', node.lineno)]
                })
            else:
                # This is a simple statement (like imports)
                main_blocks.append({
                    "type": "code",
                    "content": self._get_source_segment(node),
                    "line_range": [node.lineno, getattr(node, 'end_lineno', node.lineno)]
                })
        
        self.chunks["main"]["code_blocks"] = main_blocks
        
        # Populate all other chunks
        for chunk_id, chunk in self.chunks.items():
            if chunk_id == "main":
                continue
                
            # Find the corresponding AST node
            node = self._find_node_by_chunk_id(tree, chunk_id)
            if node:
                self._populate_chunk_content(node, chunk_id)
    
    def _find_node_by_chunk_id(self, tree: ast.AST, chunk_id: str) -> Optional[ast.AST]:
        """Find the AST node corresponding to a chunk ID"""
        # First check the main mapping
        for node, node_chunk_id in self.node_to_chunk_id.items():
            if node_chunk_id == chunk_id:
                return node
        
        # Then check the if/elif/else mapping
        for node, node_chunk_id in self.if_node_to_chunk_id.items():
            if node_chunk_id == chunk_id:
                return node
        
        # Check if it's an else chunk
        if chunk_id in self.else_chunk_to_statements:
            # For else statements, we'll handle them specially in _populate_chunk_content
            return "else_statements"
        
        return None
    
    def _populate_chunk_content(self, node: ast.AST, chunk_id: str):
        """Populate the code_blocks for a specific chunk"""
        chunk = self.chunks[chunk_id]
        
        # Handle else statements specially
        if node == "else_statements" and chunk_id in self.else_chunk_to_statements:
            statements = self.else_chunk_to_statements[chunk_id]
            blocks = []
            for stmt in statements:
                if stmt in self.node_to_chunk_id:
                    blocks.append({
                        "type": "chunk_ref",
                        "chunk_id": self.node_to_chunk_id[stmt],
                        "line_range": [stmt.lineno, getattr(stmt, 'end_lineno', stmt.lineno)]
                    })
                else:
                    blocks.append({
                        "type": "code",
                        "content": self._get_source_segment(stmt),
                        "line_range": [stmt.lineno, getattr(stmt, 'end_lineno', stmt.lineno)]
                    })
            chunk["code_blocks"] = blocks
            return
        
        if isinstance(node, ast.ClassDef):
            # Class chunk - only class declaration, everything else should be references
            blocks = [{
                "type": "code",
                "content": f"class {node.name}:",
                "line_range": [node.lineno, node.lineno]
            }]
            
            # Add references to all class members
            for item in node.body:
                if item in self.node_to_chunk_id:
                    blocks.append({
                        "type": "chunk_ref",
                        "chunk_id": self.node_to_chunk_id[item],
                        "line_range": [item.lineno, getattr(item, 'end_lineno', item.lineno)]
                    })
                else:
                    # Simple statements without their own chunks
                    blocks.append({
                        "type": "code", 
                        "content": self._get_source_segment(item),
                        "line_range": [item.lineno, getattr(item, 'end_lineno', item.lineno)]
                    })
            
            chunk["code_blocks"] = blocks
        
        elif isinstance(node, ast.FunctionDef):
            # Method or function chunk
            self._populate_function_content(node, chunk_id)
        
        elif isinstance(node, ast.If):
            # If-else container chunk
            if chunk["type"] == "if_else_block":
                blocks = []
                
                # Add if chunk reference
                if_id = f"if{chunk_id.split('if')[1].split('_')[0]}"
                blocks.append({"type": "chunk_ref", "chunk_id": if_id})
                
                # Add elif/else references
                current = node
                elif_count = 0
                while current.orelse:
                    if len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
                        elif_count += 1
                        elif_id = f"elif{elif_count}"
                        blocks.append({"type": "chunk_ref", "chunk_id": elif_id})
                        current = current.orelse[0]
                    else:
                        else_count = chunk_id.split('if')[1].split('_')[0]
                        else_id = f"else{else_count}"
                        blocks.append({"type": "chunk_ref", "chunk_id": else_id})
                        break
                
                chunk["code_blocks"] = blocks
            
            elif chunk["type"] == "if_statement":
                # Individual if chunk - get the entire if statement including condition and body
                chunk["code_blocks"] = [{
                    "type": "code",
                    "content": self._get_source_segment(node, include_body=True),
                    "line_range": [node.lineno, self._get_body_end_line(node.body)]
                }]
        
        elif isinstance(node, ast.For):
            # For loop chunk
            chunk["code_blocks"] = [{
                "type": "code",
                "content": self._get_source_segment(node, include_body=True),
                "line_range": [node.lineno, getattr(node, 'end_lineno', node.lineno)]
            }]
        
        elif isinstance(node, ast.While):
            # While loop chunk
            chunk["code_blocks"] = [{
                "type": "code",
                "content": self._get_source_segment(node, include_body=True),
                "line_range": [node.lineno, getattr(node, 'end_lineno', node.lineno)]
            }]
        
        # Add other node types as needed...
        
        # Update dependencies
        # chunk["dependencies"] = self._extract_dependencies(node)
    
    def _populate_function_content(self, node: ast.FunctionDef, chunk_id: str):
        """Populate content for function/method chunks"""
        chunk = self.chunks[chunk_id]
        blocks = []
        
        # Only add function signature as code, everything else should be references
        func_signature = f"def {node.name}({self._get_args_string(node.args)}) -> {self._get_returns_string(node)}:"
        blocks.append({
            "type": "code",
            "content": func_signature,
            "line_range": [node.lineno, node.lineno]
        })
        
        # Add references to all child chunks
        for stmt in node.body:
            if stmt in self.node_to_chunk_id:
                blocks.append({
                    "type": "chunk_ref",
                    "chunk_id": self.node_to_chunk_id[stmt],
                    "line_range": [stmt.lineno, getattr(stmt, 'end_lineno', stmt.lineno)]
                })
            else:
                # Create a simple code block for statements without their own chunks
                blocks.append({
                    "type": "code",
                    "content": self._get_source_segment(stmt),
                    "line_range": [stmt.lineno, getattr(stmt, 'end_lineno', stmt.lineno)]
                })
        
        chunk["code_blocks"] = blocks
    
    def _get_body_end_line(self, body: List[ast.AST]) -> int:
        """Get the end line of a body of statements"""
        if not body:
            return 0
        return max(getattr(stmt, 'end_lineno', stmt.lineno) for stmt in body)
    
    def _get_source_segment(self, node: ast.AST, include_body: bool = False, body_only_if: bool = False) -> str:
        """Extract source code for a given AST node"""
        start_line = node.lineno - 1
        end_line = getattr(node, 'end_lineno', node.lineno) - 1
        
        if include_body and hasattr(node, 'body') and node.body:
            if body_only_if and hasattr(node, 'test'):
                body_end = self._get_body_end_line(node.body) - 1
                end_line = body_end
            else:
                body_end = self._get_body_end_line(node.body) - 1
                end_line = max(end_line, body_end)
        
        if hasattr(node, 'end_lineno') and node.end_lineno:
            end_line = max(end_line, node.end_lineno - 1)
        
        lines = self.source_lines[start_line:end_line + 1]
        
        if lines:
            non_empty_lines = [line for line in lines if line.strip()]
            if non_empty_lines:
                min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
                cleaned_lines = []
                for line in lines:
                    if line.strip():
                        cleaned_lines.append(line[min_indent:] if len(line) > min_indent else line)
                    else:
                        cleaned_lines.append(line)
                return '\n'.join(cleaned_lines)
        
        return '\n'.join(lines)
    
    def _extract_dependencies(self, node: ast.AST) -> List[str]:
        """Extract variable dependencies from a node"""
        dependencies = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                dependencies.add(child.id)
        return list(dependencies)
    
    def _extract_top_level_definitions(self, tree: ast.AST) -> List[str]:
        """Extract top-level class and function definitions"""
        definitions = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                definitions.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                definitions.append(node.name)
        return definitions
    
    def _get_args_string(self, args: ast.arguments) -> str:
        """Convert function arguments to string"""
        arg_strs = [arg.arg for arg in args.args]
        return ", ".join(arg_strs)
    
    def _get_returns_string(self, node: ast.FunctionDef) -> str:
        """Get return type annotation as string"""
        if node.returns:
            return "ReturnType"
        return "None"
    
    def _create_error_chunk(self, source_code: str, error_msg: str) -> Dict[str, Any]:
        """Create a single chunk when parsing fails"""
        return {
            "metadata": {
                "error": True,
                "error_message": error_msg,
                "chunking_method": "error_fallback"
            },
            "chunks": {
                "main": {
                    "id": "main",
                    "type": "error",
                    "code_blocks": [{
                        "type": "code",
                        "content": source_code,
                        "line_range": [1, len(source_code.split('\n'))]
                    }],
                    # "dependencies": [],
                    # "defines": [],
                    "parent_scope": None
                }
            }
        }
    
    def _create_output_structure(self, file_path: str) -> Dict[str, Any]:
        """Create the final output structure"""
        return {
            "metadata": {
                "original_file": file_path,
                "total_chunks": len(self.chunks),
                "chunking_method": "ast_semantic",
                "timestamp": datetime.now().isoformat()
            },
            "chunks": self.chunks,
            "relationships": self._build_relationships(),
            "context_map": self._build_context_map()
        }
    
    def _build_relationships(self) -> Dict[str, Any]:
        """Build relationship mappings between chunks"""
        execution_flow = ["main"]
        dependency_graph = {}
        
        # for chunk_id, chunk in self.chunks.items():
        #     dependency_graph[chunk_id] = chunk.get("dependencies", [])
        
        return {
            "execution_flow": execution_flow,
            "dependency_graph": dependency_graph
        }
    
    def _build_context_map(self) -> Dict[str, Any]:
        """Build global context mapping"""
        return {
            "global_imports": [],
            "global_variables": [],
            "functions": [],
            "classes": []
        }


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python chunker.py <python_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    chunker = CodeChunker()
    
    try:
        result = chunker.chunk_file(file_path)
        
        output_file = file_path.replace('.py', '_chunked.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        print(f"Successfully chunked {file_path}")
        print(f"Output saved to {output_file}")
        print(f"Total chunks created: {result['metadata']['total_chunks']}")
        
    except Exception as e:
        print(f"Error chunking file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()