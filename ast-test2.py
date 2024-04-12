import ast
import pprint
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
        if isinstance(node.func, ast.Name):
            node_name += f": {node.func.id}"
    if isinstance(node, ast.Constant):
        node_name += f": {node.value}"
    dot.node(str(id(node)), node_name)
    if parent:
        dot.edge(str(id(parent)), str(id(node)))
    for child in ast.iter_child_nodes(node):
        add_node(child, node)

# Add nodes to the Digraph

code = '''
Z1 = np.random.rand(1,65536)
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
add_node(tree)

dot.format = 'png'
dot.render('my_ast2', view=True)