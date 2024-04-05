import ast
import difflib
import os
import re
from git import Repo
from urllib.parse import urlparse

def get_file_content(repo, commit, file_path):
    try:
        return commit.tree[file_path].data_stream.read().decode('utf-8')
    except KeyError:
        return None

class CodeChangeDetector(ast.NodeVisitor):
    def __init__(self, old_source, new_source):
        self.old_source = old_source
        self.new_source = new_source
        self.changes = []
    
    def detectFormatChange(self):
        diff = list(difflib.unified_diff(self.old_source.splitlines(), self.new_source.splitlines(), n=0))
        format_patterns = [
            r'%[\(\{]?[^\)\}]*[\)\}]?[sdifge]',  # % formatting with support for mapping keys
            r'\{[^\}]*\}',                       # .format() formatting
            r'\{[^\}]*:[^\}]*\}',                # .format() with format specifiers
            r'f"[^"]*"',                         # f-string
            r"f'[^']*'"                          # f-string with single quotes
        ]

        for i, line in enumerate(diff):
            if line.startswith('+') and any(re.search(pattern, line) for pattern in format_patterns):
                # Find the similar old line if it exists
                old_line_index = i - 1
                while old_line_index >= 0 and not diff[old_line_index].startswith('-'):
                    old_line_index -= 1
                old_line = diff[old_line_index] if old_line_index >= 0 else None
                old_content = old_line[1:].strip() if old_line else "No similar old line"
                new_content = line[1:].strip()
                self.changes.append(f"Detected format change in string representation:\n\tOld: {old_content}\n\tNew: {new_content}")


    def detectModifyingFilePaths(self):
        # Detect changes in file path usage
        pattern = re.compile(r'\b(?:open|Path|savefig|to_csv|to_json|save_images|load_weights)\b\(([^)]+)\)')
        old_matches = pattern.findall(self.old_source)
        new_matches = pattern.findall(self.new_source)
        
        for old_match, new_match in zip(old_matches, new_matches):
            if old_match != new_match:
                self.changes.append(f"File path modified from {old_match} to {new_match}")


    def detectFileWritingOperation(self):
        try:
            old_ast = ast.parse(self.old_source) if self.old_source else None
        except SyntaxError as error:
            self.changes.append(f"Syntax error in old source: {error}")
            old_ast = None

        try:
            new_ast = ast.parse(self.new_source)
        except SyntaxError as error:
            self.changes.append(f"Syntax error in new source: {error}")
            new_ast = None

        if not old_ast or not new_ast:
            return  # Skip further analysis if we can't parse the sources

        old_operations = self._collect_file_operations(old_ast) if old_ast else set()
        new_operations = self._collect_file_operations(new_ast)

        added_operations = new_operations - old_operations
        removed_operations = old_operations - new_operations

        for operation in added_operations:
            self.changes.append(f"Added file writing operation: {operation}")
        for operation in removed_operations:
            self.changes.append(f"Removed file writing operation: {operation}")
    
    def _collect_file_operations(self, ast_node):
        operations = set()
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ['write', 'save', 'savefig', 'to_csv', 'to_json', 'save_images']:
                operation = ast.unparse(node)
                operations.add(operation)
        return operations

    def detect_changes(self):
        self.detectFormatChange()
        self.detectModifyingFilePaths()
        self.detectFileWritingOperation()

def clone_and_analyze(repo_url, commit_hash):
    parsed_url = urlparse(repo_url)
    repo_name = parsed_url.path.split('/')[-1].replace('.git', '')
    repo_dir = os.path.join("cloned_repos", repo_name)

    if not os.path.exists(repo_dir):
        print(f"Cloning {repo_url}...")
        repo = Repo.clone_from(repo_url, repo_dir)  
    else:
        print(f"Repository {repo_name} already exists. Fetching updates...")
        repo = Repo(repo_dir)  
        repo.git.fetch()

    try:
        repo.git.checkout(commit_hash)  
    
        commit = repo.commit(commit_hash)
        parent_commit = commit.parents[0] if commit.parents else commit
    
        for diff_item in commit.diff(parent_commit, create_patch=True):
            if diff_item.a_path.endswith('.py'):
                old_content = get_file_content(repo, parent_commit, diff_item.a_path) or ""
                new_content = get_file_content(repo, commit, diff_item.a_path) or ""
                
                detector = CodeChangeDetector(old_content, new_content)
                detector.detect_changes()
                
                if detector.changes:
                    print(f"Changes detected in {diff_item.a_path}:")
                    for change in detector.changes:
                        print(f" - {change}")
                else:
                    print(f"No specific 'output data type' changes detected in {diff_item.a_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    repo_url = "https://github.com/Mappy/tf-faster-rcnn"
    commit_hash = "51e0889fbdcd4c48f31def4c1cb05a5a4db04671"
    clone_and_analyze(repo_url, commit_hash)
