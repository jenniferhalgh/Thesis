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
def what(x, y):
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

model_functions = ["fully_connected", "Dense", "what" ]

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

def findparam(node, call_funcs):
    constants = []
    variables = []
    for call_func in call_funcs:
        #print(f"call: {call_func}")
        if hasattr(call_func, 'args'):
            for arg in call_func.args:
                if isinstance(arg, ast.Name):
                    obj = {"Name": arg.id}
                    variables.append({"Name": arg.id})
        if hasattr(call_func, 'keywords'):
            for keyword in call_func.keywords:
                constant = findConstant(keyword)
                #value = find
                obj = {"keyword": keyword.arg, "value": constant}
                #print(obj)
                constants.append(obj)
    return constants, variables

def find_funcs(ast1, functions):
    funcs = []
    for node in ast.walk(ast1):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            elif isinstance(node.func, ast.Name):
                func_name = node.func.id
            
            for func in functions:
                if func_name == func:
                    funcs.append(node)
    return funcs


call_functions = find_funcs(ast1, model_functions)
constants, variables = findparam(ast1, call_functions)
vars = findAllValues(variables, ast1)

call_functions2 = find_funcs(ast2, model_functions)
constants2, variables2 = findparam(ast2, call_functions2)
vars2 = findAllValues(variables2, ast2)

"""
for element in parameters:
    print(element)

for var in variables:
    print(f'var: {var}')
"""

print(f'\nold')
for params in vars:
    print(f'paramval: {params}')
for cons in constants:
    print(f'constants: {cons}')

print(f'\nnew')
for params2 in vars2:
    print(f'paramval2: {params2}')
for cons2 in constants2:
    print(f'constants: {cons2}')




