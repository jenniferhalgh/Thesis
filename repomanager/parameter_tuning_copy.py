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
        #self.calls = pd.DataFrame(columns=['name','value'])
        self.calls = pd.DataFrame(columns=['name','node'])
        self.names = set()
    def find_Call(self, tree):
        for node in ast.walk(tree):
                
            #print("hello")
            if isinstance(node, ast.Call):
                
                name = ""
                if isinstance(node.func, ast.Attribute):
                    name = node.func.attr
                            
                elif isinstance(node.func, ast.Name):
                    name = node.func.id
                #print(ast.get_source_segment(codestr, node))
                new_row = {'name': name, 'node': str(ast.dump(node))}
                self.calls.loc[len(self.calls)] = new_row
            if isinstance(node, ast.Assign):
                    #print(node.value)
                    for child in ast.iter_child_nodes(node):
                        if isinstance(child, ast.Name):
                            name = child.id
                            new_row = {'name': name, 'node': str(ast.dump(node))}
                            self.calls.loc[len(self.calls)] = new_row
                            #print(name)

    def visit_Constant(self, node):
        
        if isinstance(node.value, (int, float)) and type(node.value) is not bool:
            parent = self._find_parent(node)
            grandparent = self._find_parent(parent)
            if not isinstance(grandparent, ast.For) and not isinstance(grandparent, ast.comprehension) and not isinstance(parent, ast.For):
                name = ""
                if isinstance(parent, ast.Call):
                    if isinstance(parent.func, ast.Attribute):
                        name = parent.func.attr
                        if isinstance(parent.func.value, ast.Name):
                                if parent.func.value.id == "parser":
                                    name = ""
                                #if parent.func.value.id == "tf" or parent.func.value.id == "slim":
                                #    name = parent.func.attr
                            
                    elif isinstance(parent.func, ast.Name):
                        name = parent.func.id
                elif isinstance(parent, ast.keyword):
                    name = parent.arg
                    grandparent = self._find_parent(parent)
                    if isinstance(grandparent, ast.Call):
                        if isinstance(grandparent.func, ast.Attribute):
                            name = grandparent.func.attr

                            if isinstance(grandparent.func.value, ast.Name):
                                ""
                                if grandparent.func.value.id == "parser":
                                    name = ""
                        elif isinstance(grandparent.func, ast.Name):
                            
                            name = grandparent.func.id
                                #if grandparent.func.value.id == "tf" or grandparent.func.value.id == "slim":
                                #    name = parent.arg
                                
                    if isinstance(grandparent, ast.FunctionDef):
                        name = grandparent.name
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
                elif isinstance(parent, ast.List):
                    grandparent = self._find_parent(parent)
                    
                    if isinstance(grandparent, ast.Call):
                        if isinstance(grandparent.func, ast.Attribute):
                            name = grandparent.func.attr
                        elif isinstance(grandparent.func, ast.Name):
                            
                            name = grandparent.func.id
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
    old_collector.find_Call(old_tree)
    new_collector.find_Call(new_tree)
    """
    for index, row in old_collector.constants.iterrows():
        print(f'name: {row["name"]}, value: {row["value"]}')
    
    for index, row in new_collector.constants.iterrows():
        print(f'name: {row["name"]}, value: {row["value"]}')
    """
    return old_collector.constants, new_collector.constants, old_collector.names, old_collector.calls, new_collector.calls
    #collector.visit(new_tree)
    #return collector.old_constants, collector.new_constants

def compare(old, new):
    param_tuning = False

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
    
    elif removed :

        #print('removals, ignoring position')
        for line in removed:
            if line not in added:
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
                return None

        if ast1 and ast2:

            old, new, names, oldcalls, newcalls = get_constants(ast1, ast2)

            """
            print("old")
            print(oldcalls)
            print("new")
            print(newcalls)
            """
            calls = []

            diff = difflib.unified_diff(oldcalls["node"].tolist(), newcalls["node"].tolist(), fromfile='file1', tofile='file2', lineterm='', n=0)
            lines = list(diff)[2:]
            added = [line[1:] for line in lines if line[0] == '+']
            removed = [line[1:] for line in lines if line[0] == '-']
            #print("added")
            #print(added)
            #print("removed")
            #print(removed)
            if added :
                names1 = []
                for linea in added:
                        index = newcalls.loc[newcalls['node'] == linea].index[0]
                        name = newcalls["name"][index]

                        for liner in removed:
                            indexr = oldcalls.loc[oldcalls['node'] == liner].index[0]
                            names1.append(oldcalls["name"][indexr])
                        if name not in names1:
                            calls.append(newcalls["name"][index])
                            
            
            
            
            if removed :
                names1 = []
                for liner in removed:
                        index = oldcalls.loc[oldcalls['node'] == liner].index[0]
                        name = oldcalls["name"][index]
                        for linea in added:
                            indexa = newcalls.loc[newcalls['node'] == linea].index[0]
                            names1.append(newcalls["name"][indexa])
                        if name not in names1:
                            calls.append(oldcalls["name"][index])
                            #calls.append(line)
            #print(calls)
            """
            if removed :
                for line in removed:
                    if line not in removed:
                        calls.append(line)
            """
            """
            if added :
                for line in added:
                    if line not in removed:
                        #print(line)
                        calls.append(line)
            """
            """
            if removed :
                for line in removed:
                    if line not in added:
                        #print(line)
                        calls.append(line)
            """
            drop_index = []
            for index2, row2 in new.iterrows():
                if new["name"][index2] not in names:
                    drop_index.append(index2)
                
                    #new.drop(index2)
            
            new.drop(drop_index, inplace=True)  # Drop the row

            drop_new = []
            for index2, row2 in new.iterrows():
                if new["name"][index2] in calls:
                    drop_new.append(index2)
            new.drop(drop_new, inplace=True)  # Drop the row

            drop_old = []
            for index2, row2 in old.iterrows():
                if old["name"][index2] in calls:
                    drop_old.append(index2)

            
            old.drop(drop_old, inplace=True)  # Drop the row
            
            
            
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
    #file = "https://github.com/google/youtube-8m/commit/f03b29494e2bf5066a63e4534ac3ce9243bfc782"
    file = "https://github.com/atriumlts/subpixel/commit/0852d4b49d38f02cf2e699a63f6b5fec63ef7ea7"
    #file = "https://github.com/google/youtube-8m/commit/0e526caace96d3cf6f0686757d568f9ffba998b4"
    repo_path, commit_hash = clone_repo(file)
    analyze = False
    df,  analyze= commit_changes(repo_path, commit_hash)
    if analyze:
        parameter_tuning(df)