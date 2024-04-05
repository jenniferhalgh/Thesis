import ast
from ast import *
import difflib
import pandas as pd
from ast_test import GlobalUseCollector
from graphviz import Digraph
dot = Digraph()

model_functions = ["fully_connected", "Dense" ]

def get_parent(node):
        for parent in ast.walk(node):
            for child in ast.iter_child_nodes(parent):
                if child == node:
                    return parent
        return None

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
                    if isinstance(arg.value, (int, float)):
                        constants.append({"Name": call_func["name"], "value": arg.value})
                        params.append({"value": arg.value})
        if hasattr(call_func["node"], 'keywords'):
            for keyword in call_func["node"].keywords:
                if isinstance(keyword.value, ast.Constant):
                    params.append({"Name": keyword.arg, "value": keyword.value.value})
                    constants.append({"Name": keyword.arg, "value": keyword.value.value})
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

def find_assignments(ast_tree):
    assignments = pd.DataFrame(columns=['name','value'])
    for node in ast.walk(ast_tree):
        if isinstance(node, ast.Assign):
            if hasattr(node, "value"):
                if isinstance(node.value, ast.Constant):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            new_row = {'name': target.id, 'value': str(node.value.value)}
                            assignments.loc[len(assignments)] = new_row
    return assignments

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

def find_def(ast_tree):
    
    defss = pd.DataFrame(columns=['name','args','constants'])
    for node in ast.walk(ast_tree):
        if isinstance(node, ast.FunctionDef):
            cons = []
            args = []
            if hasattr(node, "args"):
                if hasattr(node.args, "args"):
                    for arg in node.args.args:
                        args.append(arg.arg)

                if hasattr(node.args, "defaults"):
                    for defs in node.args.defaults:
                        if isinstance(defs, ast.Constant):
                            cons.append(str(defs.value))
            #new_row = {'name': str(node.name), 'args': str(args), 'constants': str(cons)}
            new_row = {'name': node.name, 'args': args, 'constants': cons}
            defss.loc[len(defss)] = new_row
            #defss = defss.append(new_row, ignore_index=True)
                            #print({"Name": node.name, "value": defs.value, "test": node.args.args[1].arg})
    return defss

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

def compare_assignments(assignment1, assignment2):

    for row1, row2 in zip(assignment1["value"], assignment2["value"]):
        diff = difflib.unified_diff(row1, row2, fromfile='file1', tofile='file2', lineterm='', n=0)
        lines = list(diff)[2:]

        added = [line[1:] for line in lines if line[0] == '+']
        removed = [line[1:] for line in lines if line[0] == '-']

        if added :
            print('additions, ignoring position')
            for line in added:
                if line not in removed:
                    print(line)

def compare_defs2(def1, def2):

    diff = difflib.unified_diff(def1["name"].tolist(), def2["name"].tolist(), fromfile='file1', tofile='file2', lineterm='', n=0)
    lines = list(diff)[2:]

    added = [line[1:] for line in lines if line[0] == '+']
    removed = [line[1:] for line in lines if line[0] == '-']

    if added :
        print('additions:')
        for line in added:
            print(line)

        print('additions, ignoring position')
        for line in added:
            if line not in removed:
                print(line)
    
    for row1, row2 in zip(def1["args"], def2["args"]):
        #print(row1.strip().splitlines())
        f_row1 = '\n'.join(row1)
        f_row2 = '\n'.join(row2)
        diff = difflib.unified_diff(f_row1.strip().splitlines(), f_row2.strip().splitlines(), fromfile='file1', tofile='file2', lineterm='', n=0)
        lines = list(diff)[2:]
        added = [line[1:] for line in lines if line[0] == '+']
        removed = [line[1:] for line in lines if line[0] == '-']

        if added :
            

            print('additions, ignoring position')
            for line in added:
                if line not in removed:
                    print(line)

    for val1, val2 in zip(def1["constants"], def2["constants"]):
        f_val1 = '\n'.join(val1)
        f_val2 = '\n'.join(val2)
        diff = difflib.unified_diff(f_val1.strip().splitlines(), f_val2.strip().splitlines(), fromfile='file1', tofile='file2', lineterm='', n=0)
        lines = list(diff)[2:]
        added = [line[1:] for line in lines if line[0] == '+']
        removed = [line[1:] for line in lines if line[0] == '-']

        if added :
            

            print('additions, ignoring position')
            for line in added:
                if line not in removed:
                    print(line)
    
def compare_defs(def1, def2):
    amount = len(def1)

    for i in range(amount):
        if def1[i]["Name"] == def2[i]["Name"]:
            name = def1[i]["Name"]

            len1 = len(def1[i]["args"])
            len2 = len(def2[i]["args"])

            len11 = len(def1[i]["constants"])
            len22 = len(def2[i]["constants"])
            if(len1 > len2):
                diff = len1 - len2
                for i in range(diff):
                    def2[i]["args"].append(None)
            elif (len2 > len1):
                diff = len2 - len1
                for i in range(diff):
                    def1[i]["args"].append(None)
            
            if(len11 > len22):
                diff = len11 - len22
                for i in range(diff):
                    def2[i]["constants"].append(None)
            elif (len22 > len11):
                diff = len22 - len11
                for i in range(diff):
                    def1[i]["constants"].append(None)
            
            for arg1, arg2 in zip(def1[i]["args"], def2[i]["args"]):
                #print(f"{name} 1:{arg1} 2: {arg2}")
                if arg1 != arg2:
                    print(f"{name} 1:{arg1} 2: {arg2}")
            for val1, val2 in zip(def1[i]["constants"], def2[i]["constants"]):
                if val1 != val2:
                    print(f"{name} 1:{val1} 2: {val2}")

# Load the DataFrame from the CSV file
df = pd.read_csv("./pt.csv")

for index, row in df.iterrows():
    old_ast = eval(df["oldFileContent"].iloc[index])
    current_ast = eval(df["currentFileContent"].iloc[index])

    ast1 = ast.parse(old_ast)
    ast2 = ast.parse(current_ast)

    call_functions = find_funcs(ast1)
    constants, variables, everything = findparam(call_functions)
    vars = findAllValues(variables, ast1)
    assignments = find_assignments(ast1)
    defs = find_def(ast1)

    call_functions2 = find_funcs(ast2)
    constants2, variables2, everything2 = findparam(call_functions2)
    vars2 = findAllValues(variables2, ast2)
    assignments2 = find_assignments(ast2)
    defs2 = find_def(ast2)

    compare(constants, constants2)
    compare_assignments(assignments, assignments2)
    compare_defs2(defs, defs2)
"""
print(f'\nold')
#for params in vars:
#    print(f'{params}')
for ever in everything:
    print(f'{ever}')
#for cons in constants:
#    print(f'{cons}')

print(f'\nnew')
#for params2 in vars2:
#    print(f'{params2}')
for cons2 in constants2:
    print(f'{cons2}')
"""




