import ast
from ast import *
import pandas as pd
from ast_test import GlobalUseCollector
from graphviz import Digraph
dot = Digraph()
# Define a function to recursively add nodes to the Digraph
def add_node(node, parent=None):
    node_name = str(node.__class__.__name__)
    if isinstance(node, ast.FunctionDef):
        node_name += f": {node.name}"
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            node_name += f": {node.func.attr}"
    if isinstance(node, ast.Constant):
        node_name += f": {node.value}"
    if isinstance(node, ast.keyword):
        node_name += f": {node.arg}"
    if isinstance(node, ast.Name):
        node_name += f": {node.id}"
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

model_functions = ["fully_connected", "Dense" ]

def find_parameters(ast1, ast2):
    # Initialize lists to store nodes in each AST
    parameters = []
    nodes_ast1 = []
    nodes_ast2 = []
    
    # Traverse AST1 and collect nodes
    for node in ast.walk(ast1):
        nodes_ast1.append(node)
    
    # Traverse AST2 and collect nodes
    for node in ast.walk(ast2):
        nodes_ast2.append(node)
    
    # Compare nodes between ASTs
    for node1, node2 in zip(nodes_ast1, nodes_ast2):
        # Compare node types
        if type(node1) != type(node2):
            print(f"Node type mismatch: {type(node1)} in AST1, {type(node2)} in AST2")
            continue
        
        # Compare specific attributes of interest (e.g., function names)
        if isinstance(node1, ast.Call):
            #the function call has an attribute (i.e., it's not a bare function call)
            if isinstance(node1.func, ast.Attribute):
                if node1.func.attr == "fully_connected":
                    
                    print(node1.func.attr)
    
    
        #constants = []
        if isinstance(node1, ast.Call):
            if isinstance(node1.func, ast.Attribute):
                if node1.func.attr == "fully_connected":
                    node = node1
                    for call_child in ast.iter_child_nodes(node1):
                        if isinstance(call_child, ast.keyword):
                            print(f"keyword: {call_child.arg}")
                            for child_node in ast.walk(node1):
                                if isinstance(child_node, ast.Constant):
                                    print(f"constant: {child_node.value}")
                                    obj = {"name": call_child.arg, "value": child_node.value}
                                    parameters.append(obj)
                        elif isinstance(call_child, ast.Name):
                            print(f"name: {call_child.id} ctx: {call_child.ctx}")
                                    #constants.append(child_node.value)
                            # Traverse the node's children to find constant values
        
        
        # Add more comparisons as needed
        
        # If nodes are equal, continue traversal
        # Here, you can add more specific comparisons based on the node types
        
    # Add logic to find specific function name if not found during traversal
    # You can search for the function name within the AST nodes if needed

ast1 = ast.parse(old_ast)
ast2 = ast.parse(current_ast)
parameters = []
parameters = find_parameters(ast1, ast2)




