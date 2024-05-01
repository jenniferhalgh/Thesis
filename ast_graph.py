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
class Subpixel(Conv2D):
    def __init__(self,
                 filters,
                 kernel_size,
                 r,
                 padding='valid',
                 data_format=None,
                 strides=(1,1),
                 activation=None,
                 use_bias=True,
                 kernel_initializer='glorot_uniform',
                 bias_initializer='zeros',
                 kernel_regularizer=None,
                 bias_regularizer=None,
                 activity_regularizer=None,
                 kernel_constraint=None,
                 bias_constraint=None,
                 **kwargs):
        super(Subpixel, self).__init__(
            filters=r*r*filters,
            kernel_size=kernel_size,
            strides=strides,
            padding=padding,
            data_format=data_format,
            activation=activation,
            use_bias=use_bias,
            kernel_initializer=kernel_initializer,
            bias_initializer=bias_initializer,
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            activity_regularizer=activity_regularizer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,
            **kwargs)
        self.r = r

    def _phase_shift(self, I):
        r = self.r
        bsize, a, b, c = I.get_shape().as_list()
        bsize = K.shape(I)[0] # Handling Dimension(None) type for undefined batch dim
        X = K.reshape(I, [bsize, a, b, c/(r*r),r, r]) # bsize, a, b, c/(r*r), r, r
        X = K.permute_dimensions(X, (0, 1, 2, 5, 4, 3))  # bsize, a, b, r, r, c/(r*r)
        #Keras backend does not support tf.split, so in future versions this could be nicer
        X = [X[:,i,:,:,:,:] for i in range(a)] # a, [bsize, b, r, r, c/(r*r)
        X = K.concatenate(X, 2)  # bsize, b, a*r, r, c/(r*r)
        X = [X[:,i,:,:,:] for i in range(b)] # b, [bsize, r, r, c/(r*r)
        X = K.concatenate(X, 2)  # bsize, a*r, b*r, c/(r*r)
        return X

    def call(self, inputs):
        return self._phase_shift(super(Subpixel, self).call(inputs))

    def compute_output_shape(self, input_shape):
        unshifted = super(Subpixel, self).compute_output_shape(input_shape)
        return (unshifted[0], self.r*unshifted[1], self.r*unshifted[2], unshifted[3]/(self.r*self.r))

    def get_config(self):
        config = super(Conv2D, self).get_config()
        config.pop('rank')
        config.pop('dilation_rate')
        config['filters']/=self.r*self.r
        config['r'] = self.r
        return config
'''



code2="""
model.add(TimeDistributed(Convolution2D(32, 5, 5, subsample=(2, 2), border_mode="same")))
    model.add(ELU())
"""

tree = ast.parse(code)
add_node(code, tree)

dot.format = 'png'
dot.render('my_ast2', view=True)