import ast
from ast import *
import difflib
import os
import re
import shutil
from git import Repo, InvalidGitRepositoryError
from urllib.parse import urlparse
from repo_utils import clone_repo
from repo_changes import commit_changes
import pandas as pd

def get_file_content(repo, commit, file_path):
    try:
        return commit.tree[file_path].data_stream.read().decode('utf-8')
    except KeyError:
        return None

class InputChangeDetector(ast.NodeVisitor):
    def __init__(self, old_source, new_source):
        self.old_source = old_source
        self.new_source = new_source
        self.changes = []
        self.detect_changes()

    def detect_changes(self):
        old_ast = ast.parse(self.old_source)
        new_ast = ast.parse(self.new_source)
        self.detectURLChanges(old_ast, new_ast)
        old_functions = {node.name: node for node in ast.walk(old_ast) if isinstance(node, ast.FunctionDef)}
        new_functions = {node.name: node for node in ast.walk(new_ast) if isinstance(node, ast.FunctionDef)}

        for func_name, new_func in new_functions.items():
            old_func = old_functions.get(func_name)
            if old_func:
                self.compare(old_func, new_func)

    def detectURLChanges(self, old_ast, new_ast):
        old_urls = {node.targets[0].id: node.value.s for node in ast.walk(old_ast) if isinstance(node, ast.Assign) and isinstance(node.value, ast.Str)}
        new_urls = {node.targets[0].id: node.value.s for node in ast.walk(new_ast) if isinstance(node, ast.Assign) and isinstance(node.value, ast.Str)}
        for var, old_url in old_urls.items():
            new_url = new_urls.get(var)
            if new_url and new_url != old_url:
                self.changes.append(f"URL change for {var}: from {old_url} to {new_url}")

    def compare(self, old_func, new_func):
        # Compare parameters
        old_params = [param.arg for param in old_func.args.args]
        new_params = [param.arg for param in new_func.args.args]
        if old_params != new_params:
            self.changes.append(f"Input parameter change in function '{old_func.name}' from {old_params} to {new_params}")

        # Check for changes in how inputs are handled within the function
        old_reads = [node.func.attr for node in ast.walk(old_func) if isinstance(node, ast.Call) and self.is_input_related(node)]
        new_reads = [node.func.attr for node in ast.walk(new_func) if isinstance(node, ast.Call) and self.is_input_related(node)]
        if old_reads != new_reads:
            self.changes.append(f"Change in data input handling in function '{new_func.name}' from {old_reads} to {new_reads}")

    def is_input_related(self, node):
        return isinstance(node.func, ast.Attribute) and node.func.attr in ['read', 'get', 'fetch']

def input_data(df):
    changes = False
    for index, row in df.iterrows():
        old_content = row["oldFileContent"]
        new_content = row["currentFileContent"]
        detector = InputChangeDetector(old_content, new_content)
        detector.detect_changes()

        if detector.changes:
            print(f"Changes detected in {df['Path'][index]}:")
            for change in detector.changes:
                print(f" - {change}")
            changes = True
    print(f"Changes detected: {changes}")
    return changes

if __name__ == "__main__":
    repo_path, commit_hash = clone_repo("https://github.com/thtrieu/darkflow/commit/3259b8fb7e21e8ede23f41f7358cb9d71defeb59")
    df, analyze = commit_changes(repo_path, commit_hash)
    if analyze:
        input_data(df)
