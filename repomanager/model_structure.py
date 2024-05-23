import ast
from ast import *
import difflib
import pandas as pd
from repo_changes import commit_changes
from repo_utils import clone_repo

#https://www.tensorflow.org/api_docs/python/tf/compat/v1/reduce_mean
tf_reduce_mean = ["reduce_mean"]

#taken from https://typeoverflow.com/developer/docs/tensorflow~1.15/nn 
tf_nn_functions = ["all_candidate_sampler", "approx_max_k", "approx_min_k", "atrous_conv2d", "atrous_conv2d_transpose", "avg_pool", "avg_pool1d", "avg_pool2d", "avg_pool3d", "batch_norm_with_global_normalization", "batch_normalization", "bias_add", "collapse_repeated", "compute_accidental_hits", "compute_average_loss", "conv1d", "conv1d_transpose", "conv2d", "conv2d_transpose", "conv3d", "conv3d_transpose", "conv_transpose", "convolution", "crelu", "ctc_beam_search_decoder", "ctc_greedy_decoder", "ctc_loss", "ctc_unique_labels", "depth_to_space", "depthwise_conv2d", "depthwise_conv2d_backprop_filter", "depthwise_conv2d_backprop_input", "dilation2d", "dropout", "relu", "embedding_lookup", "embedding_lookup_sparse", "erosion2d", "fixed_unigram_candidate_sampler", "fractional_avg_pool", "fractional_max_pool", "gelu", "in_top_k", "isotonic_regression", "l2_loss", "l2_normalize", "leaky_relu", "learned_unigram_candidate_sampler", "local_response_normalization", "log_poisson_loss", "log_softmax", "lrn", "max_pool", "max_pool1d", "max_pool2d", "max_pool3d", "max_pool_with_argmax", "moments", "nce_loss", "normalize_moments", "pool", "relu", "relu6", "safe_embedding_lookup_sparse", "sampled_softmax_loss", "scale_regularization_loss", "selu", "separable_conv2d", "sigmoid", "sigmoid_cross_entropy_with_logits", "silu", "softmax", "softmax_cross_entropy_with_logits", "softplus", "softsign", "space_to_batch", "space_to_depth", "sparse_softmax_cross_entropy_with_logits", "sufficient_statistics", "swish", "tanh", "top_k", "weighted_cross_entropy_with_logits", "weighted_moments", "with_space_to_batch", "zero_fraction"]

#taken from https://git.ecdf.ed.ac.uk/s1886313/tensorflow/-/tree/eb10a4c494d95e7c17ddc44ef35197d08f2f6b33/tensorflow/contrib/slim#layers
slim_layers = ["bias_add", "batch_norm", "conv2d", "conv2d_in_plane", "conv2d_transpose", "fully_connected", "avg_pool2d", "dropout", "flatten", "max_pool2d", "one_hot_encoding", "separable_conv2d", "unit_norm"]

#taken from https://www.tensorflow.org/api_docs/python/tf/keras/losses
tf_keras_losses = ["KLD", "MAE", "MAPE", "MSE", "MSLE", "binary_crossentropy", "binary_focal_crossentropy", "categorical_crossentropy", "categorical_focal_crossentropy", "categorical_hinge", "cosine_similarity", "ctc", "deserialize", "dice", "get", "hinge", "huber", "kld", "kullback_leibler_divergence", "logcosh", "mae", "mape", "mse", "msle", "poisson", "serialize", "sparse_categorical_crossentropy", "squared_hinge", "tversky"]

#https://www.tensorflow.org/versions/r1.15/api_docs/python/tf/keras/regularizers
keras_regularizer = ["l1", "l2", "l1_l2"]

#https://www.tensorflow.org/versions/r1.15/api_docs/python/tf/keras/layers
keras_layers = ["Sequential", "AbstractRNNCell", "Activation", "ActivityRegularization", "Add", "AdditiveAttention", "AlphaDropout", "Attention", "Average", "AveragePooling1D", "AveragePooling2D", "AveragePooling3D", "AvgPool1D", "AvgPool2D", "AvgPool3D", "BatchNormalization", "Bidirectional", "Concatenate", "Conv1D", "Conv2D", "Conv2DTranspose", "Conv3D", "Conv3DTranspose", "ConvLSTM2D", "Convolution1D", "Convolution2D", "Convolution2DTranspose", "Convolution3D", "Convolution3DTranspose", "Cropping1D", "Cropping2D", "Cropping3D", "CuDNNGRU", "CuDNNLSTM", "Dense", "DenseFeatures", "DepthwiseConv2D", "Dot", "Dropout", "ELU", "Embedding", "Flatten", "GRU", "GRUCell", "GaussianDropout", "GaussianNoise", "GlobalAveragePooling1D", "GlobalAveragePooling2D", "GlobalAveragePooling3D", "GlobalAvgPool1D", "GlobalAvgPool2D", "GlobalAvgPool3D", "GlobalMaxPool1D", "GlobalMaxPool2D", "GlobalMaxPool3D", "GlobalMaxPooling1D", "GlobalMaxPooling2D", "GlobalMaxPooling3D", "InputLayer", "InputSpec", "LSTM", "LSTMCell", "Lambda", "Layer", "LayerNormalization", "LeakyReLU", "LocallyConnected1D", "LocallyConnected2D", "Masking", "MaxPool1D", "MaxPool2D", "MaxPool3D", "MaxPooling1D", "MaxPooling2D", "MaxPooling3D", "Maximum", "Minimum", "Multiply", "PReLU", "Permute", "RNN", "ReLU", "RepeatVector", "Reshape", "SeparableConv1D", "SeparableConv2D", "SeparableConvolution1D", "SeparableConvolution2D", "SimpleRNN", "SimpleRNNCell", "Softmax", "SpatialDropout1D", "SpatialDropout2D", "SpatialDropout3D", "StackedRNNCells", "Subtract", "ThresholdedReLU", "TimeDistributed", "UpSampling1D", "UpSampling2D", "UpSampling3D", "Wrapper", "ZeroPadding1D", "ZeroPadding2D", "ZeroPadding3D"]

#scikit https://scikit-learn.org/stable/modules/classes.html#module-sklearn.neural_network
scikit_nn_models = ["BernoulliRBM", "MLPClassifier", "MLPRegressor", "MLPRegressor"]
class ConstantCollector(ast.NodeVisitor):
    def __init__(self, source):
        self.source = source
        self.constants = pd.DataFrame(columns=['name','value'])
        self.names = set()
        self.calls = pd.DataFrame(columns=['name','node'])
        self.classdef = pd.DataFrame(columns=['name','node'])

    def find_Call(self, node):
        for node in ast.walk(node):
            if isinstance(node, ast.ClassDef):
                name = ""
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        
                        if base.id in keras_layers:
                            name = name = f"{node.name}({base.id})"

                if name:
                    new_row = {'name': name, 'node': str(ast.dump(node))}
                    self.classdef.loc[len(self.classdef)] = new_row
            if isinstance(node, ast.Call):
                name = ""
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Attribute):
        
                            if isinstance(node.func.value.value, ast.Name):
                                
                                if node.func.value.attr == "nn" and node.func.value.value.id == "tf":
                                    if node.func.attr in tf_nn_functions:
                                        name = f"{node.func.value.value.id}.{node.func.value.attr}.{node.func.attr}"

                            if isinstance(node.func.value.value, ast.Attribute):
                                if isinstance(node.func.value.value.value, ast.Name):
                                    if node.func.value.value.value.id == "tf" and node.func.value.value.attr == "keras":
                                        if node.func.value.attr == "losses" and node.func.attr in tf_keras_losses:
                                            name = f"{node.func.value.value.value.id}.{node.func.value.value.attr}.{node.func.value.attr}.{node.func.attr}"
                                        if node.func.value.attr == "layers" and node.func.attr in keras_layers:
                                            name = f"{node.func.value.value.value.id}.{node.func.value.value.attr}.{node.func.value.attr}.{node.func.attr}"
                                        if node.func.value.attr == "regularizers" and node.func.attr in keras_regularizer:
                                            name = f"{node.func.value.value.value.id}.{node.func.value.value.attr}.{node.func.value.attr}.{node.func.attr}"

                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id == "slim" and node.func.attr in slim_layers:
                                name = f"{node.func.value.id}.{node.func.attr}"
                        if node.func.value.id == "tf" and node.func.attr in tf_reduce_mean:
                                name = f"{node.func.value.id}.{node.func.attr}"
                        if node.func.value.id == "layers" and node.func.attr in keras_layers:
                                name = f"{node.func.value.id}.{node.func.attr}"
                        if node.func.value.id == "losses" and node.func.attr in tf_keras_losses:
                                name = f"{node.func.value.id}.{node.func.attr}"
                        if node.func.value.id == "regularizers" and node.func.attr in keras_regularizer:
                                name = f"{node.func.value.id}.{node.func.attr}"
                if isinstance(node.func, ast.Name):
                    if node.func.id in scikit_nn_models:
                        name = f"{node.func.id}"
                if name:
                    new_row = {'name': name, 'node': str(ast.dump(node))}
                    self.calls.loc[len(self.calls)] = new_row
    
    def _find_parent(self, node):
        for n in ast.walk(self.source):
            for child in ast.iter_child_nodes(n):
                if child == node:
                    return n
        return None
        


def get_constants(old_tree, new_tree):
    old_collector = ConstantCollector(old_tree)
    old_collector.visit(old_tree)
    new_collector = ConstantCollector(new_tree)
    new_collector.visit(new_tree)
    
    return old_collector.constants, new_collector.constants, old_collector.names

def compare_call(oldcalls, newcalls):
    diff = difflib.unified_diff(oldcalls["node"].tolist(), newcalls["node"].tolist(), fromfile='file1', tofile='file2', lineterm='', n=0)
    lines = list(diff)[2:]
    added = [line[1:] for line in lines if line[0] == '+']
    removed = [line[1:] for line in lines if line[0] == '-']
    if added :
        for linea in added:
            index = newcalls.loc[newcalls['node'] == linea].index[0]
            name = newcalls["name"][index]
            print(f"Added: {name}")
    if removed :
        for liner in removed:
            index = oldcalls.loc[oldcalls['node'] == liner].index[0]
            name = oldcalls["name"][index]
            print(f"Removed: {name}")
    if added or removed:
        return True
    else:
        return False

def compare_cd(oldcd, newcd):
    diff = difflib.unified_diff(oldcd["node"].tolist(), newcd["node"].tolist(), fromfile='file1', tofile='file2', lineterm='', n=0)
    lines = list(diff)[2:]
    added = [line[1:] for line in lines if line[0] == '+']
    removed = [line[1:] for line in lines if line[0] == '-']
    if added :
        for linea in added:
            index = newcd.loc[newcd['node'] == linea].index[0]
            name = newcd["name"][index]
            print(f"Added: {name}")
    if removed :
        for liner in removed:
            index = oldcd.loc[oldcd['node'] == liner].index[0]
            name = oldcd["name"][index]
            print(f"Removed: {name}")
    if added or removed:
        return True
    else:
        return False
    

def model_structure(df):
    changes = False
    count = 0
    for index, row in df.iterrows():
        #print("hello")
        try:
            ast1 = ast.parse(df["oldFileContent"].iloc[index])
            ast2 = ast.parse(df["currentFileContent"].iloc[index])
        except SyntaxError as e:
                ast1 = None
                ast2 = None
                print(f"SyntaxError occurred while parsing file {df['Path'][index]}: {e}")
        old_detector = ConstantCollector(ast1)
        new_detector = ConstantCollector(ast2)
        old_detector.find_Call(ast1)
        new_detector.find_Call(ast2)
        old_calls = old_detector.calls
        new_calls = new_detector.calls
        old_cd = old_detector.classdef
        new_cd = new_detector.classdef
        istrue_calls = compare_call(old_calls, new_calls)
        istrue_cd = compare_cd(old_cd, new_cd)
        if istrue_calls or istrue_cd:
            count = count + 1
    if count>0:
        changes = True
    print(changes)
    return changes


if __name__ == "__main__":
    file = "https://github.com/altairlight/DeepLabCut/commit/84004cac758ae528a71e77c213b92edecb234bb7"
    repo_path, commit_hash, username, repo_name = clone_repo(file)
    df, analyze = commit_changes(repo_path, commit_hash, username, repo_name)
    model_structure(df)