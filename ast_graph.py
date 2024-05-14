import ast
import pprint
from graphviz import Digraph
import pandas as pd
dot = Digraph()
# Define a function to recursively add nodes to the Digraph
def add_node(code, node, parent=None):
    node_name = str(node.__class__.__name__)
    if isinstance(node, ast.Expr):
        node_name += f": {node.value}"
    if isinstance(node, ast.FunctionDef):
        node_name += f": {node.name}"
    if isinstance(node, ast.Call):
        print(ast.get_source_segment(code, node))
        if isinstance(node.func, ast.Attribute):
            node_name += f": {node.func.attr}"
            if isinstance(node.func.value, ast.Name):
                node_name += f": {node.func.value.id}"
            if isinstance(node.func.value, ast.Attribute):
                node_name += f": {node.func.value.attr}"
        if isinstance(node.func, ast.Name):
            node_name += f": {node.func.id}"
    if isinstance(node, ast.Name):
        node_name += f": {node.id}"
    if isinstance(node, ast.Constant):
        node_name += f": {node.value}"
    dot.node(str(id(node)), node_name)
    if parent:
        dot.edge(str(id(parent)), str(id(node)))
    for child in ast.iter_child_nodes(node):
        add_node(code, child, node)

# Add nodes to the Digraph

code = '''
def build(self, rgb, train=False, num_classes=20, random_init_fc8=False,
              debug=False):
              print("hello")
'''



code2="""
ambiguous_pixels = tf.not_equal(labels, params.n_classes)
"""

tree = ast.parse(code)
add_node(code, tree)
modified_files = []
old_file_content = ast.dump(tree)
modified_files.append(
                {"Path": "test", "oldFileContent": old_file_content})
df = pd.DataFrame(modified_files)
df.to_csv("pt.csv", index=False)
dot.format = 'png'
dot.render('my_ast2', view=True)