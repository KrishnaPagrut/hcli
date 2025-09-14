#!/usr/bin/env python3
"""
File Diff Tool
Compares two files and shows differences with line numbers, additions, deletions, and changes.
"""

import sys
import argparse
from typing import List, Tuple, Dict, Any
from difflib import unified_diff, SequenceMatcher
from dataclasses import dataclass
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
    context: str = ""

class FileDiffer:
    def __init__(self, file1_path: str, file2_path: str):
        self.file1_path = file1_path
        self.file2_path = file2_path
        self.file1_lines = []
        self.file2_lines = []
        
    def load_files(self) -> bool:
        """Load both files into memory."""
        try:
            with open(self.file1_path, 'r', encoding='utf-8') as f:
                self.file1_lines = f.readlines()
            with open(self.file2_path, 'r', encoding='utf-8') as f:
                self.file2_lines = f.readlines()
            return True
        except FileNotFoundError as e:
            print(f"Error: File not found - {e}")
            return False
        except Exception as e:
            print(f"Error reading files: {e}")
            return False
    
    def get_detailed_diff(self) -> List[DiffResult]:
        """Get detailed differences between the two files."""
        if not self.load_files():
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
    
    def print_detailed_diff(self, show_unchanged: bool = False):
        """Print detailed differences with line numbers."""
        results = self.get_detailed_diff()
        
        if not results:
            return
        
        changes_found = False
        
        for result in results:
            if result.change_type == ChangeType.UNCHANGED and not show_unchanged:
                continue
                
            changes_found = True
            
            if result.change_type == ChangeType.UNCHANGED:
                print(f" {result.original_content}")
            elif result.change_type == ChangeType.ADDED:
                print(f"+{result.modified_content}")
            elif result.change_type == ChangeType.REMOVED:
                print(f"-{result.original_content}")
            elif result.change_type == ChangeType.CHANGED:
                print(f"-{result.original_content}")
                print(f"+{result.modified_content}")
        
        if not changes_found:
            print("No differences found between the files.")
    
    def print_summary(self):
        """Print a summary of changes."""
        results = self.get_detailed_diff()
        
        if not results:
            return
        
        added = sum(1 for r in results if r.change_type == ChangeType.ADDED)
        removed = sum(1 for r in results if r.change_type == ChangeType.REMOVED)
        changed = sum(1 for r in results if r.change_type == ChangeType.CHANGED)
        unchanged = sum(1 for r in results if r.change_type == ChangeType.UNCHANGED)
        
        print(f"\n{'='*50}")
        print("SUMMARY")
        print(f"{'='*50}")
        print(f"Total lines in {self.file1_path}: {len(self.file1_lines)}")
        print(f"Total lines in {self.file2_path}: {len(self.file2_lines)}")
        print(f"Lines added: {added}")
        print(f"Lines removed: {removed}")
        print(f"Lines changed: {changed}")
        print(f"Lines unchanged: {unchanged}")
        print(f"Total differences: {added + removed + changed}")
    
    def print_unified_diff(self):
        """Print unified diff format."""
        if not self.load_files():
            return
        
        diff = unified_diff(
            self.file1_lines,
            self.file2_lines,
            fromfile=self.file1_path,
            tofile=self.file2_path,
            lineterm=''
        )
        
        print(f"\n{'='*80}")
        print("UNIFIED DIFF FORMAT")
        print(f"{'='*80}")
        
        for line in diff:
            print(line)

def main():
    parser = argparse.ArgumentParser(description='Compare two files and show differences')
    parser.add_argument('file1', help='First file (original)')
    parser.add_argument('file2', help='Second file (modified)')
    parser.add_argument('--show-unchanged', '-u', action='store_true', 
                       help='Show unchanged lines')
    parser.add_argument('--unified', action='store_true',
                       help='Show unified diff format')
    parser.add_argument('--summary', '-s', action='store_true',
                       help='Show only summary')
    
    args = parser.parse_args()
    
    differ = FileDiffer(args.file1, args.file2)
    
    if args.unified:
        differ.print_unified_diff()
    elif args.summary:
        differ.print_summary()
    else:
        differ.print_detailed_diff(args.show_unchanged)

if __name__ == "__main__":
    main()
