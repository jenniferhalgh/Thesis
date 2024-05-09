import ast
import difflib
import pandas as pd
from repo_utils import clone_repo
from repo_changes import commit_changes

# Updated input_functions with detailed tracking of library functions
input_functions = {
    'cv2': ['imread', 'VideoCapture', 'imdecode'], # Opencv, used in image and video analysis applications
    'np': ['load', 'loadtxt', 'fromstring', 'frombuffer', 'genfromtxt'],# NumPy to laod and manipulate datasets in numerical formats
    'pipe_in': ['stdin', 'stdout', 'stderr'], #sys module
    'misc': ['imread'], # misc deal with image data
    'os': ['makedirs'], # os module managing data access 
    'os.path': ['join', 'exists', 'isdir']
}

class CodeChangeDetector(ast.NodeVisitor):
    def __init__(self, source):
        self.source = source
        self.calls = pd.DataFrame(columns=['name', 'node'])

    def find_Call(self, node):
        for node in ast.walk(node):
            if isinstance(node, ast.Call):
                name = ""
                current = node.func
                components = []
                while isinstance(current, ast.Attribute):
                    components.append(current.attr)
                    current = current.value
                if isinstance(current, ast.Name):
                    components.append(current.id)
                    components.reverse()
                    function_name = '.'.join(components)
                    # Check for os.path specific functions
                    if function_name.startswith('os.path.'):
                        sub_function = function_name.split('.')[-1]
                        if sub_function in input_functions['os.path']:
                            name = function_name
                    elif any(function_name.startswith(lib + '.') and function_name.split('.')[1] in funcs for lib, funcs in input_functions.items() if lib != 'os.path'):
                        name = function_name
                if name:
                    new_row = {'name': name, 'node': str(ast.dump(node))}
                    self.calls.loc[len(self.calls)] = new_row

    def visit_Call(self, node):
        self.find_Call(node)
        self.generic_visit(node)

def compare(oldcalls, newcalls):
    diff = difflib.unified_diff(
        oldcalls["node"].tolist(), newcalls["node"].tolist(), fromfile='file1', tofile='file2', lineterm='', n=0
    )
    lines = list(diff)[2:]
    added = [line[1:] for line in lines if line[0] == '+']
    removed = [line[1:] for line in lines if line[0] == '-']
    if added or removed:
        for linea in added:
            index = newcalls.loc[newcalls['node'] == linea].index[0]
            print(f"Added: {newcalls['name'][index]}")
        for liner in removed:
            index = oldcalls.loc[oldcalls['node'] == liner].index[0]
            print(f"Removed: {oldcalls['name'][index]}")
        return True
    return False

def input_data(df):
    changes = False
    count = 0
    for index, row in df.iterrows():
        old_content = row["oldFileContent"]
        new_content = row["currentFileContent"]
        old_ast = ast.parse(old_content)
        new_ast = ast.parse(new_content)
        old_detector = CodeChangeDetector(old_content)
        new_detector = CodeChangeDetector(new_content)
        old_detector.find_Call(old_ast)
        new_detector.find_Call(new_ast)
        old_calls = old_detector.calls
        new_calls = new_detector.calls
        istrue = compare(old_calls, new_calls)
        if istrue:
            count += 1
    if count > 0:
        changes = True
    print(changes)
    return changes

if __name__ == "__main__":
    repo_path, commit_hash = clone_repo("https://github.com/lsheiba/CapsNet-Tensorflow-1/commit/7c80553e049ab43aa3726d9353c3c63e71712487")
    df, analyze = commit_changes(repo_path, commit_hash)
    if analyze:
        input_data(df)
