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
        node_name += f": {node.func}"
    if isinstance(node, ast.Attribute):
        node_name += f": {node.attr}"
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

code1 = """
def what(x, y):
    a = x + y
    a = a + 1
    return a

def addThem(num):
    num = 2
    what(num)
"""

code2 = """
def what(x, y, z):
    a = x + y
    a = a + 1
    return a

def addThem(num):
    num = 3
    what(num)
"""
ast1 = ast.parse(old_ast)
ast2 = ast.parse(current_ast)
code1_ast = ast.parse(code1)
add_node(old_ast)

dot.format = 'png'
dot.render('old_ast', view=True)

model_functions = ["fully_connected", "Dense" ]

"""
print(ast.dump(ast.parse('a = 1'), indent=4))
Module(
    body=[
        Assign(
            targets=[
                Name(id='a', ctx=Store())],
            value=Constant(value=1))],
    type_ignores=[])
"""
"""
def compareParams(vars1, vars2):
    for old in vars1:
        for new in vars2:
"""

def findAllValues(variables, ast1):
    params = []
    for var in variables:
        #print(f"varname: {var['Name']}")
        for child in ast.walk(ast1):
            if isinstance(child, ast.Assign):
                if isinstance(child.value, ast.Constant):
                    for target in child.targets:
                        if isinstance(target, ast.Name) and target.id == var['Name']:
                                params.append({"Name": target.id, "val": child.value.value})
    return params


def findConstant(node):
    for child in ast.walk(node):
        if isinstance(child, ast.Constant):
            return child.value

def findparam(call_funcs):
    
    constants = []
    variables = []
    everything = []
    for call_func in call_funcs:
        params = []
        if hasattr(call_func["node"], 'args'):
            
            for arg in call_func["node"].args:
                if isinstance(arg, ast.Name):
                    variables.append({"Name": arg.id})
                if isinstance(arg, ast.Constant):
                    constants.append({"Name": call_func["name"], "value": arg.value})
                    params.append({"value": arg.value})
        if hasattr(call_func["node"], 'keywords'):
            for keyword in call_func["node"].keywords:
                if isinstance(keyword.value, ast.Call):
                    if isinstance(keyword.value.func, ast.Attribute):
                        func_name = keyword.value.func.attr
                    elif isinstance(keyword.value.func, ast.Name):
                        func_name = keyword.value.func.id
                    params.append({"Name": keyword.arg, "value": func_name})
                    constants.append({"Name": keyword.arg, "value": func_name})
                if isinstance(keyword.value, ast.Name):
                    params.append({"Name": keyword.arg, "value": keyword.value.id})
                    constants.append({"Name": keyword.arg, "value": keyword.value.id})
        
        everything.append({"function": call_func["name"], "params": params})
    return constants, variables, everything

#Find all call functions
def find_funcs(ast_tree):
    funcs = []
    for node in ast.walk(ast_tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            elif isinstance(node.func, ast.Name):
                func_name = node.func.id      
            funcs.append({"name": func_name, "node": node})                 
    return funcs

def compare(constants1, constants2):
    amount = len(constants1)
    count = 0
    for i in range(amount):
        if constants1[i]["Name"] == constants2[i]["Name"] and constants1[i]["value"] == constants2[i]["value"]:
            count = count + 1
        else:
            print(f"1: {constants1[i]} 2: {constants2[i]}")

    if amount != count:
        print("Parameter tuning")

call_functions = find_funcs(ast1)
constants, variables, everything = findparam(call_functions)
vars = findAllValues(variables, ast1)

call_functions2 = find_funcs(ast2)
constants2, variables2, everything2 = findparam(call_functions2)
vars2 = findAllValues(variables2, ast2)

"""
for element in parameters:
    print(element)

for var in variables:
    print(f'var: {var}')
"""

print(f'\nold')
for params in vars:
    print(f'{params}')
for cons in constants:
    print(f'{cons}')

print(f'\nnew')
for params2 in vars2:
    print(f'{params2}')
for cons2 in constants2:
    print(f'{cons2}')

"""
for ever in everything:
    print(f'{ever}')
"""
compare(constants, constants2)






