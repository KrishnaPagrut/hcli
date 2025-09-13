import ast
import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List


class PyToPyh(ast.NodeVisitor):
    """
    Walks through the AST of a Python file and extracts chunks
    (imports, functions, classes, etc.), then maps them to JSON
    with both raw code and pseudocode (pyh style).
    """

    def __init__(self, source: str):
        self.source = source.splitlines()
        self.chunks: List[Dict[str, Any]] = []

    def _get_code(self, node: ast.AST) -> str:
        """Extract raw code for the given AST node using line numbers."""
        return "\n".join(self.source[node.lineno - 1: node.end_lineno])

    def _make_id(self, node: ast.AST) -> str:
        """Stable ID using hash of node type + line span."""
        raw = f"{type(node).__name__}:{node.lineno}-{node.end_lineno}"
        return hashlib.md5(raw.encode()).hexdigest()[:8]

    def _add_chunk(self, node: ast.AST, chunk_type: str, name: str = None, pyh: str = None):
        """Store chunk as JSON dict."""
        chunk = {
            "id": self._make_id(node),
            "type": chunk_type,
            "name": name,
            "code": self._get_code(node),
            "pyh": pyh or self._to_pseudocode(node)
        }
        self.chunks.append(chunk)

    def _to_pseudocode(self, node: ast.AST) -> str:
        """Generate very basic pseudocode (pyh) from AST nodes."""
        if isinstance(node, ast.FunctionDef):
            header = f"def {node.name}({', '.join([arg.arg for arg in node.args.args])}):"
            body = []
            for stmt in node.body:
                body.append(self._stmt_to_pseudocode(stmt, indent=4))
            return header + "\n" + "\n".join(body)

        elif isinstance(node, ast.ClassDef):
            header = f"class {node.name}:"
            body = []
            for stmt in node.body:
                body.append(self._stmt_to_pseudocode(stmt, indent=4))
            return header + "\n" + "\n".join(body)

        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            return self._get_code(node)

        return self._get_code(node)

    def _stmt_to_pseudocode(self, stmt: ast.AST, indent: int = 0) -> str:
        pad = " " * indent
        if isinstance(stmt, ast.If):
            return pad + f"if {ast.unparse(stmt.test)}:"
        elif isinstance(stmt, ast.For):
            return pad + f"for each {ast.unparse(stmt.target)} in {ast.unparse(stmt.iter)}:"
        elif isinstance(stmt, ast.Assign):
            targets = ", ".join([ast.unparse(t) for t in stmt.targets])
            return pad + f"set {targets} to {ast.unparse(stmt.value)}"
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            return pad + f"call {ast.unparse(stmt.value.func)} with args {', '.join([ast.unparse(arg) for arg in stmt.value.args])}"
        elif isinstance(stmt, ast.Return):
            return pad + f"return {ast.unparse(stmt.value)}"
        else:
            return pad + ast.unparse(stmt)

    # Visitors
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._add_chunk(node, "function", node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        self._add_chunk(node, "class", node.name)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        self._add_chunk(node, "import")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        self._add_chunk(node, "import")
        self.generic_visit(node)


def parse_file(filepath: str, outpath: str = None):
    source = Path(filepath).read_text()
    tree = ast.parse(source)
    parser = PyToPyh(source)
    parser.visit(tree)

    result = parser.chunks
    json_str = json.dumps(result, indent=2)

    if outpath:
        Path(outpath).write_text(json_str)
    return json_str


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Parse Python into AST JSON with pseudocode.")
    parser.add_argument("file", help="Path to Python file to parse")
    parser.add_argument("-o", "--out", help="Path to save JSON output", default=None)
    args = parser.parse_args()

    output = parse_file(args.file, args.out)
    print(output)
