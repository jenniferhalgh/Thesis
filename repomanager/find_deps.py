import ast
import inspect
import pandas as pd
from ast import *
def find_dependencies(ast_tree):
    dependencies = set()

    def visit(node):
        if isinstance(node, ast.Name):
            dependencies.add(node.id)
        elif isinstance(node, ast.FunctionDef):
            dependencies.add(node.name)
            for n in node.body:
                visit(n)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                dependencies.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                dependencies.add(node.func.attr)
        elif isinstance(node, ast.Attribute):
            dependencies.add(node.attr)

    for node in ast.walk(ast_tree):
        visit(node)

    return dependencies

# Example usage
def my_function(x):
    y = x + 1
    z = helper_function(y)
    return z

def helper_function(a):
    return a * 2

df = pd.read_csv("./pt.csv")
old_ast = eval(df["oldFileContent"].iloc[0])
current_ast = eval(df["currentFileContent"].iloc[0])

ast1 = ast.parse(old_ast)
ast2 = ast.parse(current_ast)

dependencies = find_dependencies(ast1)
print(dependencies)
