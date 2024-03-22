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
    if isinstance(node, ast.Constant):
        node_name += f": {node.value}"
    dot.node(str(id(node)), node_name)
    if parent:
        dot.edge(str(id(parent)), str(id(node)))
    for child in ast.iter_child_nodes(node):
        add_node(child, node)

# Add nodes to the Digraph

code = '''
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Resizing, Dropout
from keras.applications import vgg16
from keras.callbacks import EarlyStopping
from keras import regularizers
#Done by: Jennifer
def train_model_v2(num_classes, X_train, y_train, X_val, y_val):
   
    vgg=vgg16.VGG16(weights='imagenet', include_top=False, input_shape=(224,224,3))
    for layer in vgg.layers:
        layer.trainable = False

    model = Sequential()
    model.add(vgg)
    model.add(Flatten())
    model.add(Dense(512, activation='relu'))
    model.add(Dense(num_classes, activation='softmax', kernel_regularizer=regularizers.l1_l2(0.1)))
    model.compile(optimizer="adam", loss='categorical_crossentropy', metrics=['accuracy'])
    early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
   
    history = model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=20, batch_size=10, callbacks=[early_stopping])
    return model, history
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

tree = ast.parse(code2)
add_node(tree)

dot.format = 'png'
dot.render('my_ast2', view=True)