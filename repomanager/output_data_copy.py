import ast
from ast import *
import astunparse
import difflib
import os
import re
import shutil
from git import Repo, InvalidGitRepositoryError
from urllib.parse import urlparse
from repo_utils import clone_repo
from repo_changes import commit_changes
import pandas as pd

class CodeChangeDetector(ast.NodeVisitor):
    def __init__(self, source):
        self.source = source
        self.oldtfsum = []
        self.newtfsum = []
        self.changes = []
        self.calls = pd.DataFrame(columns=['name','node'])

    def find_Call(self, node):
        for node in ast.walk(node):
            
            if isinstance(node, ast.Call):
                name = ""
                if isinstance(node.func, ast.Attribute):
                    #print(node.func.attr)
                    if node.func.attr in ['write', 'savefig', 'to_csv', 'to_json', 'save_images']:
                        name = f"{node.func.attr}"
                    if isinstance(node.func.value, ast.Attribute):
                        if node.func.value.attr == "summary":
                            if isinstance(node.func.value.value, ast.Name):
                                if node.func.value.value.id == "tf":
                                    name = f"{node.func.value.value.id}.{node.func.value.attr}.{node.func.attr}"
                        
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id == "tf" and node.func.attr == "name_scope":
                            name = f"{node.func.value.id}.{node.func.attr}"
                        if node.func.value.id == "cv2" and node.func.attr == "imwrite":
                            name = f"{node.func.value.id}.{node.func.attr}"
                        if node.func.value.id == "metrics":
                            name = f"{node.func.value.id}.{node.func.attr}"
                       
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['write', 'savefig', 'to_csv', 'to_json', 'save_images']:
                        #print(node.func.id)
                        name = f"{node.func.id}"

                        
                #elif isinstance(node.func, ast.Name):
                #    name = node.func.id
                        #print(ast.get_source_segment(codestr, node))
                if name:
                    new_row = {'name': name, 'node': str(ast.dump(node))}
                    self.calls.loc[len(self.calls)] = new_row
        
    
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
                operation = ast.dump(node)
                operations.add(operation)
        return operations
    
    def detect_tf_name_scope_changes(self):
        """
        Detects changes related to the introduction, removal, or modification of tf.name_scope.
        """
        old_name_scopes = self._collect_tf_name_scope_usages(self.old_source)
        new_name_scopes = self._collect_tf_name_scope_usages(self.new_source)

        added_name_scopes = new_name_scopes - old_name_scopes
        removed_name_scopes = old_name_scopes - new_name_scopes

        for scope in added_name_scopes:
            self.changes.append(f"Added TensorFlow name scope: {scope}")
        for scope in removed_name_scopes:
            self.changes.append(f"Removed TensorFlow name scope: {scope}")

    def _collect_tf_name_scope_usages(self, source_code):
        """
        Collects TensorFlow name scope usages from the source code.
        """
        scopes = set()
        try:
            parsed_ast = ast.parse(source_code)
            for node in ast.walk(parsed_ast):
                if isinstance(node, ast.With) and isinstance(node.items[0].context_expr, ast.Call):
                    call_node = node.items[0].context_expr
                    if (isinstance(call_node.func, ast.Attribute) and 
                        call_node.func.attr == 'name_scope' and
                        isinstance(call_node.func.value, ast.Name) and
                        call_node.func.value.id == 'tf'):
                        try:
                            scope_name = ast.literal_eval(call_node.args[0])
                            scopes.add(scope_name)
                        except ValueError:
                            # Handle cases where scope name is not a simple string literal
                            pass
                        except IndexError:
                            # Handle cases where scope name is not a simple string literal
                            pass
        except SyntaxError as e:
            # Handle syntax errors in parsing, which might occur with incompatible Python code
            pass
        return scopes
    
    def detectPrint(self):
        
        # Patterns to identify logging or print statements
        logging_patterns = [
            r'\bprint\(',
            r'\blogging\.\w+\('
        ]
        
        diff = list(difflib.unified_diff(self.old_source.splitlines(), self.new_source.splitlines(), n=0))
        
        for line in diff:
            if line.startswith('+') and any(re.search(pattern, line) for pattern in logging_patterns):
                line_number = self._get_line_number_for_added_line(diff, line)
                self.changes.append(f"Added logging or print statement: {line.strip()} at line {line_number}")

    def _get_line_number_for_added_line(self, diff, added_line):
        
        line_count = 0
        for line in diff:
            if line.startswith(' '):
                line_count += 1
            elif line == added_line:
                return line_count + 1 
        return "Unknown line number"  
    
    

    

    def detect_changes(self):
        self.detectFormatChange()
        self.detectModifyingFilePaths()
        self.detectFileWritingOperation()
        self.detect_tf_name_scope_changes()
        self.detectPrint()

def compare(oldcalls, newcalls):
    diff = difflib.unified_diff(oldcalls["node"].tolist(), newcalls["node"].tolist(), fromfile='file1', tofile='file2', lineterm='', n=0)
    lines = list(diff)[2:]
    added = [line[1:] for line in lines if line[0] == '+']
    removed = [line[1:] for line in lines if line[0] == '-']
            #print("added")
            #print(added)
            #print("removed")
            #print(removed)
    if added :
        for linea in added:
            index = newcalls.loc[newcalls['node'] == linea].index[0]
            name = newcalls["name"][index]
            print(f"Added: {name}")
    if removed :
        for liner in removed:
            index = oldcalls.loc[oldcalls['node'] == liner].index[0]
            name = oldcalls["name"][index]
            print(f"Removed: {name}")
    if added or removed:
        return True
    else:
        return False

def output_data(df):
    changes = False
    for index, row in df.iterrows():
        old_content = df["oldFileContent"].iloc[index]
        new_content = df["currentFileContent"].iloc[index]
        ast1 = ast.parse(old_content)
        ast2 = ast.parse(new_content)
        #detector = CodeChangeDetector(old_content, new_content)
        #detector.detect_changes()
        old_detector = CodeChangeDetector(old_content)
        new_detector = CodeChangeDetector(new_content)
        old_detector.find_Call(ast1)
        new_detector.find_Call(ast2)
        old_calls = old_detector.calls
        new_calls = new_detector.calls
        #print(old_calls)
        changes = compare(old_calls, new_calls)
        """
        if len(detector.changes)!=0:
            print(f"Changes detected in {df['Path'][index]}:")
            for change in detector.changes:
                print(f" - {change}")
            changes = True
        else:
            print(f"No specific 'output data type' changes detected in {df['Path'][index]}.")
            print("")
        """
    
    print(changes)
    return changes

if __name__ == "__main__":
    
    #repo_url = "https://github.com/Mappy/tf-faster-rcnn"
    #commit_hash = "51e0889fbdcd4c48f31def4c1cb05a5a4db04671"
    #repo_url = "https://github.com/Mappy/tf-faster-rcnn"
    #commit_hash = "29aefedc73be3d7419ba72802f347e372382db7d"
    #repo_url = "https://github.com/thtrieu/darkflow"
    #commit_hash = "ea141f91e59e8b8da92e2292f00bb601e0e69008"
    #repo_url = "https://github.com/atriumlts/subpixel"
    #commit_hash = "0852d4b49d38f02cf2e699a63f6b5fec63ef7ea7"
    #repo_url = "https://github.com/jakeret/tf_unet"
    #commit_hash = "9f0e79b6a38c0bbb26d674d83851e18ca0f379cc"
    #repo_url = "https://github.com/google/youtube-8m"
    #commit_hash = "462baeeb1209e3add9ed728c4b0f9dd6dde9ba9b"
    #repo_url = "https://github.com/andrewb-ms/fast-style-transfer"
    #commit_hash = "47c993b71e2fe717e21fc3da4e8e69261832ca85"
    repo_path, commit_hash = clone_repo("https://github.com/davidsandberg/facenet/commit/ebd41534269cfb55961e0cc738380abb60807f9c")
    df, analyze = commit_changes(repo_path, commit_hash)
    #print(df)
    if analyze : 
        output_data(df)
    