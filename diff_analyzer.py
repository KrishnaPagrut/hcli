#!/usr/bin/env python3
"""
Diff Analyzer
Combines file diffing and AST mapping to output changes in JSON format.
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Set, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
from enum import Enum

class ChangeType(Enum):
    ADDED = "added"
    REMOVED = "removed"
    CHANGED = "changed"
    UNCHANGED = "unchanged"

@dataclass
class DiffResult:
    line_num: int
    change_type: ChangeType
    original_content: str
    modified_content: str

@dataclass
class OutputLineMapping:
    line_number: int
    node_id: str
    node_type: str
    signature: str
    description: str
    line_range: Optional[Tuple[int, int]]
    content: str

@dataclass
class ChangeAnalysis:
    node_id: str
    node_type: str
    signature: str
    description: str
    line_range: Optional[Tuple[int, int]]
    change_type: str
    affected_output_lines: List[int]
    original_content: str
    modified_content: str

class DiffAnalyzer:
    def __init__(self, ast_json_file: str, file1_path: str, file2_path: str):
        self.ast_json_file = ast_json_file
        self.file1_path = file1_path
        self.file2_path = file2_path
        self.ast_data = None
        self.output_line_mappings = []
        self.file1_lines = []
        self.file2_lines = []
        
    def load_files(self) -> bool:
        """Load both files and AST data."""
        try:
            # Load files
            with open(self.file1_path, 'r', encoding='utf-8') as f:
                self.file1_lines = f.readlines()
            with open(self.file2_path, 'r', encoding='utf-8') as f:
                self.file2_lines = f.readlines()
            
            # Load AST
            with open(self.ast_json_file, 'r', encoding='utf-8') as f:
                self.ast_data = json.load(f)
            
            if "phy_chunks" not in self.ast_data or "main" not in self.ast_data["phy_chunks"]:
                raise ValueError("Invalid .pyh JSON: missing phy_chunks/main")
            
            return True
        except Exception as e:
            print(f"Error loading files: {e}")
            return False
    
    def get_detailed_diff(self) -> List[DiffResult]:
        """Get detailed differences between the two files."""
        if not self.file1_lines or not self.file2_lines:
            return []
        
        results = []
        matcher = SequenceMatcher(None, self.file1_lines, self.file2_lines)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Lines are the same
                for idx in range(i2 - i1):
                    results.append(DiffResult(
                        line_num=i1 + idx + 1,
                        change_type=ChangeType.UNCHANGED,
                        original_content=self.file1_lines[i1 + idx].rstrip(),
                        modified_content=self.file2_lines[j1 + idx].rstrip()
                    ))
            elif tag == 'delete':
                # Lines deleted from file1
                for idx in range(i2 - i1):
                    results.append(DiffResult(
                        line_num=i1 + idx + 1,
                        change_type=ChangeType.REMOVED,
                        original_content=self.file1_lines[i1 + idx].rstrip(),
                        modified_content=""
                    ))
            elif tag == 'insert':
                # Lines added to file2
                for idx in range(j2 - j1):
                    results.append(DiffResult(
                        line_num=j1 + idx + 1,
                        change_type=ChangeType.ADDED,
                        original_content="",
                        modified_content=self.file2_lines[j1 + idx].rstrip()
                    ))
            elif tag == 'replace':
                # Lines changed
                max_len = max(i2 - i1, j2 - j1)
                for idx in range(max_len):
                    orig_line = self.file1_lines[i1 + idx].rstrip() if i1 + idx < i2 else ""
                    mod_line = self.file2_lines[j1 + idx].rstrip() if j1 + idx < j2 else ""
                    
                    results.append(DiffResult(
                        line_num=i1 + idx + 1,
                        change_type=ChangeType.CHANGED,
                        original_content=orig_line,
                        modified_content=mod_line
                    ))
        
        return results
    
    def build_output_line_mappings(self):
        """Build mappings from output lines to AST nodes by simulating the render process."""
        if not self.ast_data:
            return
        
        self.output_line_mappings = []
        root = self.ast_data["phy_chunks"]["main"]
        
        def render_node_with_mapping(node, indent=0, line_counter=[0]):
            """Render node and track line mappings."""
            lines = []
            pad = "    " * indent

            sig = node.get("signature")
            desc = node.get("description")
            line_range = node.get("line_range")
            node_id = node.get("id", "")
            node_type = node.get("type", "")

            # Line info
            line_info = ""
            if line_range:
                line_info = f"  (lines {line_range[0]}–{line_range[1]})"

            # Show signature
            if sig:
                line_counter[0] += 1
                content = f"{pad}{sig}{line_info}"
                lines.append(content)
                
                # Map this line to the AST node
                self.output_line_mappings.append(OutputLineMapping(
                    line_number=line_counter[0],
                    node_id=node_id,
                    node_type=node_type,
                    signature=sig,
                    description=desc,
                    line_range=tuple(line_range) if line_range else None,
                    content=content
                ))
                
                if desc:
                    line_counter[0] += 1
                    content = f"{pad}    {desc}"
                    lines.append(content)
                    
                    # Map this line to the same AST node (it's the description)
                    self.output_line_mappings.append(OutputLineMapping(
                        line_number=line_counter[0],
                        node_id=node_id,
                        node_type=node_type,
                        signature=sig,
                        description=desc,
                        line_range=tuple(line_range) if line_range else None,
                        content=content
                    ))
            elif desc:
                line_counter[0] += 1
                content = f"{pad}{desc}{line_info}"
                lines.append(content)
                
                # Map this line to the AST node
                self.output_line_mappings.append(OutputLineMapping(
                    line_number=line_counter[0],
                    node_id=node_id,
                    node_type=node_type,
                    signature=sig,
                    description=desc,
                    line_range=tuple(line_range) if line_range else None,
                    content=content
                ))

            # Recurse into children
            for child in node.get("children", []):
                lines.extend(render_node_with_mapping(child, indent + 1, line_counter))

            return lines
        
        # Build the mappings
        render_node_with_mapping(root)
    
    def find_ast_node_for_output_line(self, output_line_num: int) -> Optional[OutputLineMapping]:
        """Find the AST node that corresponds to a specific output line."""
        for mapping in self.output_line_mappings:
            if mapping.line_number == output_line_num:
                return mapping
        return None
    
    def analyze_changes(self) -> List[ChangeAnalysis]:
        """Analyze changes and map them to AST nodes."""
        if not self.load_files():
            return []
        
        # Get diff results
        diff_results = self.get_detailed_diff()
        
        # Build output line mappings
        self.build_output_line_mappings()
        
        # Map changes to AST nodes
        changes = []
        processed_node_ids = set()
        
        for diff_result in diff_results:
            if diff_result.change_type == ChangeType.UNCHANGED:
                continue
            
            # Find the AST node for this output line
            mapping = self.find_ast_node_for_output_line(diff_result.line_num)
            
            if mapping and mapping.node_id not in processed_node_ids:
                change_analysis = ChangeAnalysis(
                    node_id=mapping.node_id,
                    node_type=mapping.node_type,
                    signature=mapping.signature,
                    description=mapping.description,
                    line_range=mapping.line_range,
                    change_type=diff_result.change_type.value,
                    affected_output_lines=[diff_result.line_num],
                    original_content=diff_result.original_content,
                    modified_content=diff_result.modified_content
                )
                changes.append(change_analysis)
                processed_node_ids.add(mapping.node_id)
        
        return changes
    
    def to_json(self, changes: List[ChangeAnalysis]) -> str:
        """Convert changes to JSON format."""
        # Convert dataclasses to dictionaries
        changes_dict = []
        for change in changes:
            change_dict = asdict(change)
            # Convert line_range tuple to list for JSON serialization
            if change_dict['line_range']:
                change_dict['line_range'] = list(change_dict['line_range'])
            changes_dict.append(change_dict)
        
        result = {
            "file1": self.file1_path,
            "file2": self.file2_path,
            "ast_file": self.ast_json_file,
            "total_changes": len(changes_dict),
            "changes": changes_dict,
            "metadata": {
                "source_file": "/Users/krishnapagrut/Developer/hcli/test.ast.json"
            }
        }
        
        return json.dumps(result, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Analyze file differences and map to AST nodes')
    parser.add_argument('ast_json', help='AST JSON file (.json)')
    parser.add_argument('file1', help='First file (original)')
    parser.add_argument('file2', help='Second file (modified)')
    parser.add_argument('--output', '-o', help='Output JSON file (optional)')
    
    args = parser.parse_args()
    
    # Analyze changes
    analyzer = DiffAnalyzer(args.ast_json, args.file1, args.file2)
    changes = analyzer.analyze_changes()
    
    # Convert to JSON
    json_output = analyzer.to_json(changes)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"Analysis written to {args.output}")
    else:
        print(json_output)

if __name__ == "__main__":
    main()
