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
        self.names = set()

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)) and type(node.value) is not bool:
            parent = self._find_parent(node)
            
            name = ""
            if isinstance(parent, ast.Call):
                grandparent = self._find_parent(parent)
                #print(grandparent)
                if not isinstance(grandparent, ast.For):
                    if isinstance(parent.func, ast.Attribute):
                        name = parent.func.attr
                    elif isinstance(parent.func, ast.Name):
                        #print(node.value)
                        name = parent.func.id
                        #print(name)
            elif isinstance(parent, ast.keyword):
                name = parent.arg
            elif isinstance(parent, ast.arguments):
                parent = self._find_parent(parent)
                if isinstance(parent, ast.FunctionDef):
                    name = parent.name
            elif isinstance(parent, ast.Assign):
                #print(node.value)
                for child in ast.walk(parent):
                    if isinstance(child, ast.Name):
                        name = child.id
                        #print(name)
                

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
    
    """
    for index, row in old_collector.constants.iterrows():
        print(f'name: {row["name"]}, value: {row["value"]}')
    
    for index, row in new_collector.constants.iterrows():
        print(f'name: {row["name"]}, value: {row["value"]}')
    """
    return old_collector.constants, new_collector.constants, old_collector.names
    #collector.visit(new_tree)
    #return collector.old_constants, collector.new_constants

def compare(old, new):
    param_tuning = False
    """
    diff = difflib.unified_diff(old["name"].tolist(), new["name"].tolist(), fromfile='file1', tofile='file2', lineterm='', n=0)
    lines = list(diff)[2:]

    added = [line[1:] for line in lines if line[0] == '+']
    removed = [line[1:] for line in lines if line[0] == '-']

    if added :

        print('additions, ignoring position')
        for line in added:
            if line not in removed:
                print(line)
    """

    diff = difflib.unified_diff(old["value"].tolist(), new["value"].tolist(), fromfile='file1', tofile='file2', lineterm='', n=0)
    lines = list(diff)[2:]
    added = [line[1:] for line in lines if line[0] == '+']
    removed = [line[1:] for line in lines if line[0] == '-']

    if added :
            

        #print('additions, ignoring position')
        for line in added:
            if line not in removed:
                print(line)
                param_tuning = True

    return param_tuning
    

def parameter_tuning(df):
    #df = pd.read_csv("./pt.csv")
    #print(len(df))
    count = 0
    for index, row in df.iterrows():
        #print("hello")
        try:
            ast1 = ast.parse(df["oldFileContent"].iloc[index])
            ast2 = ast.parse(df["currentFileContent"].iloc[index])
        except SyntaxError as e:
                ast1 = None
                ast2 = None
                print(f"SyntaxError occurred while parsing file {df['Path'][index]}: {e}")

        if ast1 and ast2:
            old, new, names = get_constants(ast1, ast2)
            
            for index2, row2 in new.iterrows():
                if new["name"][index2] not in names:
                    new.drop(index2)
            #print("names")
            #print(names)
            #print("old")
            #print(old)
            #print("new")
            #print(new)
            result = compare(old, new)
            if result:
                count = count + 1
    if count > 0:
        param = True
    else:
        param = False
    return param


if __name__ == "__main__":
    file = "https://github.com/paulcarfantan/neural-style/commit/664509b899ded951716a102022c2b2744e4af3ca"
    repo_path, commit_hash = clone_repo(file)
    df = commit_changes(repo_path, commit_hash)
    parameter_tuning(df)