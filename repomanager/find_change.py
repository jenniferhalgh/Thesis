import ast
from ast import *
import pandas as pd
from ast_test import GlobalUseCollector
from graphviz import Digraph
dot = Digraph()
# Define a function to recursively add nodes to the Digraph
def add_node(node, parent=None):
    node_name = str(node.__class__.__name__)
    dot.node(str(id(node)), node_name)
    if parent:
        dot.edge(str(id(parent)), str(id(node)))
    for child in ast.iter_child_nodes(node):
        add_node(child, node)

# Load the DataFrame from the CSV file
df = pd.read_csv("./pt.csv")
# Iterate over the rows of the DataFrame
old_ast = eval(df["oldFileContent"].iloc[0])
current_ast = eval(df["currentFileContent"].iloc[0])

add_node(old_ast)

dot.format = 'png'
dot.render('old_ast', view=True)


