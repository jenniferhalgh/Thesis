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
import astor

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
      self.detectListChanges(old_ast, new_ast)
      self.detectVariableDeletions(old_ast, new_ast)
      
      old_functions = {node.name: node for node in ast.walk(old_ast) if isinstance(node, ast.FunctionDef)}
      new_functions = {node.name: node for node in ast.walk(new_ast) if isinstance(node, ast.FunctionDef)}

      for func_name, old_func in old_functions.items():
        new_func = new_functions.get(func_name)
        if new_func:
            self.compare(old_func, new_func)
        elif 'fps' in old_func.name:  # Example of a specific keyword to identify functions
            self.changes.append(f"Function related to FPS '{func_name}' was removed.")




    def detectURLChanges(self, old_ast, new_ast):
         old_urls = {}
         new_urls = {}
         for node in ast.walk(old_ast):
           if isinstance(node, ast.Assign) and isinstance(node.value, ast.Str):
              for target in node.targets:
                if isinstance(target, ast.Name):  
                    old_urls[target.id] = node.value.s

         for node in ast.walk(new_ast):
           if isinstance(node, ast.Assign) and isinstance(node.value, ast.Str):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    new_urls[target.id] = node.value.s

         for var, old_url in old_urls.items():
          new_url = new_urls.get(var)
          if new_url and new_url != old_url:
            self.changes.append(f"URL change for {var}: from {old_url} to {new_url}")
    
    def detectListChanges(self, old_ast, new_ast):
    # Focus on lists that are likely to contain image data or paths
      def is_image_related_list(list_name):
        keywords = ['path', 'file', 'photo', 'picture']
        return any(keyword in list_name.lower() for keyword in keywords)

      old_lists = self.extract_lists(old_ast)
      new_lists = self.extract_lists(new_ast)

      for list_var in old_lists:
        if list_var in new_lists and old_lists[list_var] != new_lists[list_var] and is_image_related_list(list_var):
            self.changes.append(f"Image-related list change for {list_var}: from {old_lists[list_var]} to {new_lists[list_var]}")
        elif list_var not in new_lists and is_image_related_list(list_var):
            self.changes.append(f"Image-related list {list_var} removed in new version")

    def extract_lists(self, ast_node):
      list_dict = {}
      for node in ast.walk(ast_node):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    list_contents = [elem.n if isinstance(elem, ast.Num) else elem.s if isinstance(elem, ast.Str) else None for elem in node.value.elts]
                    list_dict[target.id] = list_contents
      return list_dict



    def detectVariableDeletions(self, old_ast, new_ast):
    # Broaden the criteria to include general processing variables
      def is_critical_image_processing_var(var_name):
        # Include both explicit image-related keywords and common processing terms
        image_keywords = ['path']
        processing_keywords = ['samples']  
        return any(keyword in var_name.lower() for keyword in image_keywords + processing_keywords)

      old_vars = {node.id for node in ast.walk(old_ast) if isinstance(node, ast.Name)}
      new_vars = {node.id for node in ast.walk(new_ast) if isinstance(node, ast.Name)}

      deleted_vars = old_vars - new_vars
      for var in deleted_vars:
        if is_critical_image_processing_var(var):
            self.changes.append(f"Critical variable deleted: {var}")

    def compare(self, old_func, new_func):
      old_method_calls = self.extract_method_calls(old_func)
      new_method_calls = self.extract_method_calls(new_func)

      for method in set(old_method_calls.keys()).union(new_method_calls.keys()):
        old_kwargs = old_method_calls.get(method, {})
        new_kwargs = new_method_calls.get(method, {})
        
        for key in set(old_kwargs.keys()).union(new_kwargs.keys()):
            old_value = old_kwargs.get(key, 'None')  # Default to 'None' if not present
            new_value = new_kwargs.get(key, 'None')
            if old_value != new_value:
                self.changes.append(f"Change detected in method '{method}' for keyword '{key}': from {old_value} to {new_value}")

    def extract_method_calls(self, func_node):
      method_calls = {}
      for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            method_name = ''
            if isinstance(node.func, ast.Attribute):
                method_name = node.func.attr
            elif isinstance(node.func, ast.Name):
                method_name = node.func.id

            # Specifically focus on np.load calls
            if method_name == 'load': 
                kwargs = {}
                for kw in node.keywords:
                    kwargs[kw.arg] = astor.to_source(kw.value).strip()
                method_calls[method_name] = kwargs

      return method_calls
    
def input_data(df):
    changes = False
    count = 0
    for index, row in df.iterrows():
        old_content = row["oldFileContent"]
        new_content = row["currentFileContent"]
        detector = InputChangeDetector(old_content, new_content)
        detector.detect_changes()

        if detector.changes:
            print(f"Changes detected in {df['Path'][index]}:")
            for change in detector.changes:
                print(f" - {change}")
            istrue = True
            if istrue:
                count = count + 1
    if count > 0:
        changes = True
    else:
        changes = False
    print(f"Changes detected: {changes}")
    return changes

if __name__ == "__main__":
    repo_path, commit_hash = clone_repo("https://github.com/lengstrom/fast-style-transfer/commit/ffdec65daf2e323f9577f402120270e4c53ccc00")
    df, analyze = commit_changes(repo_path, commit_hash)
    if analyze:
        input_data(df)
