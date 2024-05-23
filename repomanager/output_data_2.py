import ast
from ast import *
import astunparse
import difflib
import os
import re
import shutil
from git import Repo, InvalidGitRepositoryError
from urllib.parse import urlparse
from repo_utils import clone_repo
from repo_changes import commit_changes
import pandas as pd

#taken from https://numpy.org/doc/stable/reference/routines.io.html
numpy_output = ["save", "savez", "savez_compressed", "savetxt", "ndarray.tofile", "memmap"]

#taken from https://docs.opencv.org/3.4/d4/da8/group__imgcodecs.html
opencv_writing = ["imwrite", "imwritemulti", "imencode"]

#taken from https://scikit-learn.org/stable/modules/classes.html#module-sklearn.metrics
sklearn_metrics = ["accuracy_score", "auc", "average_precision_score", "balanced_accuracy_score", "brier_score_loss", "class_likelihood_ratios", "classification_report", "cohen_kappa_score", "confusion_matrix", "dcg_score", "det_curve", "f1_score", "fbeta_score", "hamming_loss", "hinge_loss", "jaccard_score", "log_loss", "matthews_corrcoef", "multilabel_confusion_matrix", "ndcg_score", "precision_recall_curve", "precision_recall_fscore_support", "precision_score", "recall_score", "roc_auc_score", "roc_curve", "top_k_accuracy_score", "zero_one_loss"]

#taken from https://www.tensorflow.org/versions/r1.15/api_docs/python/tf/summary
tf_summary = ["all_v2_summary_ops", "audio", "get_summary_description", "histogram", "image", "initialize", "merge", "merge_all", "scalar", "tensor_summary", "text"]

matplotlib = ["savefig"]

class CodeChangeDetector(ast.NodeVisitor):
    def __init__(self, source):
        self.source = source
        self.oldtfsum = []
        self.newtfsum = []
        self.changes = []
        self.calls = pd.DataFrame(columns=['name','node'])

    def find_Call(self, node):
        for node in ast.walk(node):
            
            if isinstance(node, ast.Call):
                name = ""
                if isinstance(node.func, ast.Attribute):
                    #print(node.func.attr)
                    if isinstance(node.func.value, ast.Attribute):
                            if isinstance(node.func.value.value, ast.Name):
                                if node.func.value.attr == "summary" and node.func.value.value.id == "tf":
                                    if node.func.attr in tf_summary:
                                        name = f"{node.func.value.value.id}.{node.func.value.attr}.{node.func.attr}"
                        
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id == "cv2" and node.func.attr in opencv_writing:
                            name = f"{node.func.value.id}.{node.func.attr}"
                        if node.func.value.id == "metrics" and node.func.attr in sklearn_metrics:
                            name = f"{node.func.value.id}.{node.func.attr}"
                        if node.func.value.id == "np" and node.func.attr in numpy_output:
                            name = f"{node.func.value.id}.{node.func.attr}"
                        if node.func.value.id == "tf" and node.func.attr == "name_scope":
                            name = f"{node.func.value.id}.{node.func.attr}"
                        if node.func.value.id == "plt" and node.func.attr in matplotlib:
                            name = f"{node.func.value.id}.{node.func.attr}"
                       
                if name:
                    new_row = {'name': name, 'node': str(ast.dump(node))}
                    self.calls.loc[len(self.calls)] = new_row

def compare(oldcalls, newcalls):
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

def output_data(df):
    changes = False
    count = 0
    for index, row in df.iterrows():
        old_content = df["oldFileContent"].iloc[index]
        new_content = df["currentFileContent"].iloc[index]
        ast1 = ast.parse(old_content)
        ast2 = ast.parse(new_content)
        old_detector = CodeChangeDetector(old_content)
        new_detector = CodeChangeDetector(new_content)
        old_detector.find_Call(ast1)
        new_detector.find_Call(ast2)
        old_calls = old_detector.calls
        new_calls = new_detector.calls
        istrue = compare(old_calls, new_calls)

        if istrue:
            count = count + 1
    if count>0:
        changes = True
    print(changes)
    return changes

if __name__ == "__main__":
    file = "https://github.com/Mappy/tf-faster-rcnn/commit/29aefedc73be3d7419ba72802f347e372382db7d"
    repo_path, commit_hash, username, repo_name = clone_repo(file)
    df, analyze = commit_changes(repo_path, commit_hash, username, repo_name)
    if analyze : 
        output_data(df)
    
