"""
import ast
import pprint
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

# Add nodes to the Digraph

code1 = '''
def load_image(path):
    def load_image(path):
        img = cv2.imread(path,-1)
        if len(img.shape)==2:
            image = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        else:
            image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return image
'''

code2 = '''
def load_image(path):
    def load_image(path):
        img = cv2.imread(path,-1)
        if len(img.shape)==2:
            image = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        else:
            image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return image
'''

tree = ast.parse(code2)

for node in ast.walk(tree): #traverses through the tree
    if isinstance(node, ast.Call): #checks if the node is a function call
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == 'cv2':
            if node.func.attr == 'cvtColor':
                print("Pre-processing")
            else:
                print("nothing")
            
add_node(tree)

dot.format = 'png'
dot.render('my_ast', view=True)
"""
import ast

class GlobalUseCollector(ast.NodeVisitor):
    def __init__(self, name):
        self.name = name
        # track context name and set of names marked as `global`
        self.context = [('global', ())]

    def visit_FunctionDef(self, node):
        self.context.append(('function', set()))
        self.generic_visit(node)
        self.context.pop()

    # treat coroutines the same way
    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.context.append(('class', ()))
        self.generic_visit(node)
        self.context.pop()

    def visit_Lambda(self, node):
        # lambdas are just functions, albeit with no statements, so no assignments
        self.context.append(('function', ()))
        self.generic_visit(node)
        self.context.pop()

    def visit_Global(self, node):
        assert self.context[-1][0] == 'function'
        self.context[-1][1].update(node.names)

    def visit_Name(self, node):
        ctx, g = self.context[-1]
        if node.id == self.name and (ctx == 'global' or node.id in g):
            print('{} used at line {}'.format(node.id, node.lineno))

u = ast.parse('''\
x = 20

def g():
    global x
    x = 0
    for x in range(10):
        x += 10
    return x

g()
for x in range(10):
    pass
x += 1
print(x)
''')
#GlobalUseCollector('x').visit(u)