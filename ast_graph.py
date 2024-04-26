import ast
import pprint
from graphviz import Digraph
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
auc = metrics.auc(fpr, tpr)
'''



code2="""
class FrameLevelLogisticModel(models.BaseModel):
  def create_model(self, model_input, vocab_size, num_frames, **unused_params):
    num_frames = tf.cast(tf.expand_dims(num_frames, 1), tf.float32)
    feature_size = model_input.get_shape().as_list()[2]
    denominators = tf.reshape(
        tf.tile(num_frames, [1, feature_size]), [-1, feature_size])
    avg_pooled = tf.reduce_sum(model_input,
                               axis=[1]) / denominators

    output = slim.fully_connected(
        avg_pooled, vocab_size, activation_fn=tf.nn.sigmoid,
        weights_regularizer=slim.l2_regularizer(1e-8))
    return {"predictions": output}
"""

tree = ast.parse(code)
add_node(code, tree)

dot.format = 'png'
dot.render('my_ast2', view=True)