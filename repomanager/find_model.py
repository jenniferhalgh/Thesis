import ast
from ast import *
import pandas as pd
from ast_test import GlobalUseCollector
from graphviz import Digraph
import pyan
from IPython.display import HTML


dot = Digraph()

# Define a function to recursively add nodes to the Digraph
def add_node(node, parent=None):
    node_name = str(node.__class__.__name__)
    if isinstance(node, ast.FunctionDef):
        node_name += f": {node.name}"
    if isinstance(node, ast.Call):
        node_name += f": {node.func}"
    if isinstance(node, ast.Attribute):
        node_name += f": {node.attr}"
    #if isinstance(node, ast.Constant):
    #    node_name += f": {node.value}"
    #if isinstance(node, ast.keyword):
    #    node_name += f": {node.arg}"
    if isinstance(node, ast.Name):
        node_name += f": {node.id}"
    dot.node(str(id(node)), node_name)
    if parent:
        dot.edge(str(id(parent)), str(id(node)))
    for child in ast.iter_child_nodes(node):
        add_node(child, node)

df = pd.read_csv("./pt.csv")
# Iterate over the rows of the DataFrame
old_ast = eval(df["oldFileContent"].iloc[1])
current_ast = eval(df["currentFileContent"].iloc[1])
    
ast1 = ast.parse(old_ast)
ast2 = ast.parse(current_ast)
add_node(old_ast)

dot.format = 'png'
dot.render('old_ast', view=True)

def find_parent(ast_tree, target_node):
    parent_stack = []
    found = False
    
    def traverse(node, parent):
        nonlocal found
        if node == target_node:
            found = True
            return parent
        for child in ast.iter_child_nodes(node):
            result = traverse(child, node)
            if result:
                return result
        return None
    
    parent_node = traverse(ast_tree, None)
    if found:
        return parent_node
    else:
        return None


def find_funcs(ast_tree):
    funcs = []
    for node in ast.walk(ast_tree):
            if isinstance(node, ast.Name) and node.id == 'tf':
                func_name = node.id
                #funcs.append({"name": func_name, "node": node})            
                funcs.append(node)                 
    return funcs



functions = find_funcs(ast1)

for func in functions:
    target_node = func # The node for which you want to find the parent
    parent_node = find_parent(ast1, target_node)
    print(f"{func.id}.{parent_node.attr}")
