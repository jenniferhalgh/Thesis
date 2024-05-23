import ast
from ast import *
import difflib
import pandas as pd
from repo_changes import commit_changes
from repo_utils import clone_repo
        

class ConstantCollector(ast.NodeVisitor):
    def __init__(self, source):
        self.source = source
        self.constants = pd.DataFrame(columns=['name','value'])
        self.functiondefs = pd.DataFrame(columns=['name','value'])
        self.calls = []
        self.callnodes = []
        self.names = set()

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)) and type(node.value) is not bool:
            parent = self._find_parent(node)
            grandparent = self._find_parent(parent)
            if not isinstance(grandparent, ast.For) and not isinstance(grandparent, ast.comprehension) and not isinstance(parent, ast.For):
                name = ""
                if isinstance(parent, ast.Call):
                    self.callnodes.append(parent)
                    if isinstance(parent.func, ast.Attribute):
                        if isinstance(parent.func.value, ast.Name):
                                if parent.func.value.id == "tf" or parent.func.value.id == "slim":
                                    name = parent.func.attr
                        
                    elif isinstance(parent.func, ast.Name):
                        name = parent.func.id
                elif isinstance(parent, ast.keyword):
                    grandparent = self._find_parent(parent)
                    if isinstance(grandparent, ast.Call):
                        if isinstance(grandparent.func, ast.Attribute):
                            if isinstance(grandparent.func.value, ast.Name):
                                if grandparent.func.value.id == "parser":
                                    name = ""
                                if grandparent.func.value.id == "tf" or grandparent.func.value.id == "slim":
                                    name = parent.arg
                    if isinstance(grandparent, ast.FunctionDef):
                        name = grandparent.name
                elif isinstance(parent, ast.arguments):
                    parent = self._find_parent(parent)
                    if isinstance(parent, ast.FunctionDef):
                        name = parent.name
                elif isinstance(parent, ast.Assign):

                    for child in ast.walk(parent):
                        if isinstance(child, ast.Name):
                            name = child.id

                elif isinstance(parent, ast.List):
                    grandparent = self._find_parent(parent)
                    
                    if isinstance(grandparent, ast.Call):
                        if isinstance(grandparent.func, ast.Attribute):
                            name = grandparent.func.attr
                        elif isinstance(grandparent.func, ast.Name):
                            
                            name = grandparent.func.id

                    
                    

                if name:
                    new_row = {'name': name, 'value': str(node.value)}
                    self.constants.loc[len(self.constants)] = new_row
                    self.names.add(name)
    
    def _find_parent(self, node):
        for n in ast.walk(self.source):
            for child in ast.iter_child_nodes(n):
                if child == node:
                    return n
        return None
        


def get_constants(old_tree, new_tree):
    old_collector = ConstantCollector(old_tree)
    old_collector.visit(old_tree)
    new_collector = ConstantCollector(new_tree)
    new_collector.visit(new_tree)

    return old_collector.constants, new_collector.constants, old_collector.names

def compare(old, new):
    param_tuning = False

    diff = difflib.unified_diff(old["value"].tolist(), new["value"].tolist(), fromfile='file1', tofile='file2', lineterm='', n=0)
    lines = list(diff)[2:]
    added = [line[1:] for line in lines if line[0] == '+']
    removed = [line[1:] for line in lines if line[0] == '-']

    if added :
        for line in added:
            if line not in removed:
                print(line)
                param_tuning = True
    
    elif removed :
        for line in removed:
            if line not in added:
                print(line)
                param_tuning = True
    
    return param_tuning


def parameter_tuning(df):
    count = 0
    for index, row in df.iterrows():
        try:
            ast1 = ast.parse(df["oldFileContent"].iloc[index])
            ast2 = ast.parse(df["currentFileContent"].iloc[index])
        except SyntaxError as e:
                ast1 = None
                ast2 = None
                print(f"SyntaxError occurred while parsing file {df['Path'][index]}: {e}")
                return None

        if ast1 and ast2:

            old, new, names = get_constants(ast1, ast2)
            
            drop_index = []
            for index2, row2 in new.iterrows():
                if new["name"][index2] not in names:
                    drop_index.append(index2)
            
            new.drop(drop_index, inplace=True)
            result = compare(old, new)
            if result:
                count = count + 1
    if count > 0:
        param = True
    else:
        param = False
    return param


if __name__ == "__main__":
    file = "https://github.com/atriumlts/subpixel/commit/0852d4b49d38f02cf2e699a63f6b5fec63ef7ea7"
    repo_path, commit_hash = clone_repo(file)
    df = commit_changes(repo_path, commit_hash)
    parameter_tuning(df)