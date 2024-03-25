import ast

code1 = '''
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
'''

code2 = '''
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
        weights_regularizer=slim.l2_regularizer(1e-5))
    return {"predictions": output}
'''

tree1 = ast.parse(code1)
tree2 = ast.parse(code2)

for node in ast.walk(tree2): #traverses through the tree
    if isinstance(node, ast.Call): #checks if the node is a function call
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == 'cv2':
            if node.func.attr == 'cvtColor':
                print("Pre-processing")
            else:
                print("nothing")
"""
def find_regularizer_differences(node1, node2, lineno=1):
    if isinstance(node1, ast.Call) and isinstance(node2, ast.Call):
        print("call")
        if isinstance(node1.func, ast.Attribute) and isinstance(node2.func, ast.Attribute):
            print("attr")
            print(node1.func.attr)
            print(node2.func.attr)
            if node1.func.attr == "fully_connected" and node2.func.attr == "fully_connected":
                print("yes")
                for kwarg1, kwarg2 in zip(node1.keywords, node2.keywords):
                    if kwarg1.arg == "weights_regularizer" and kwarg2.arg == "weights_regularizer":
                        if isinstance(kwarg1.value, ast.Call) and isinstance(kwarg2.value, ast.Call):
                            if isinstance(kwarg1.value.func, ast.Attribute) and isinstance(kwarg2.value.func, ast.Attribute):
                                if kwarg1.value.func.attr != kwarg2.value.func.attr:
                                    print(f"Difference in regularizer values at line {lineno}: {kwarg1.value.func.attr} (in code1) vs {kwarg2.value.func.attr} (in code2)")

    elif isinstance(node1, ast.AST) and isinstance(node2, ast.AST):
        print("no")
        for child_node1, child_node2 in zip(ast.iter_child_nodes(node1), ast.iter_child_nodes(node2)):
            find_regularizer_differences(child_node1, child_node2, lineno)

find_regularizer_differences(tree1, tree2)
"""