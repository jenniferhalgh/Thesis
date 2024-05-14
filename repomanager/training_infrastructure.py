import ast
from ast import *
import difflib
import pandas as pd
from repo_changes import commit_changes
from repo_utils import clone_repo

#taken from https://typeoverflow.com/developer/docs/tensorflow~1.15/train
tf_train_functions = ["MonitoredTrainingSession", "NewCheckpointReader", "add_queue_runner", "assert_global_step", "basic_train_loop", "batch", "batch_join", "checkpoint_exists", "checkpoints_iterator", "cosine_decay", "cosine_decay_restarts", "create_global_step", "do_quantize_training_on_graphdef", "exponential_decay", "export_meta_graph", "generate_checkpoint_state_proto", "get_checkpoint_mtimes", "get_checkpoint_state", "get_global_step", "get_or_create_global_step", "global_step", "import_meta_graph", "init_from_checkpoint", "input_producer", "inverse_time_decay", "latest_checkpoint", "limit_epochs", "linear_cosine_decay", "list_variables", "load_checkpoint", "load_variable", "match_filenames_once", "maybe_batch", "maybe_batch_join", "maybe_shuffle_batch", "maybe_shuffle_batch_join", "natural_exp_decay", "noisy_linear_cosine_decay", "piecewise_constant", "piecewise_constant_decay", "polynomial_decay", "range_input_producer", "remove_checkpoint", "replica_device_setter", "sdca_fprint", "sdca_optimizer", "sdca_shrink_l1", "shuffle_batch", "shuffle_batch_join", "slice_input_producer", "start_queue_runners", "string_input_producer", "summary_iterator", "update_checkpoint_state", "warm_start", "write_graph"]

#https://docs.python.org/3/library/argparse.html

class ConstantCollector(ast.NodeVisitor):
    def __init__(self, source):
        self.source = source
        self.constants = pd.DataFrame(columns=['name','value'])
        self.names = set()
        self.calls = pd.DataFrame(columns=['name','node'])

    def find_Call(self, node):
        for node in ast.walk(node):
            
            if isinstance(node, ast.Call):
                name = ""
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Attribute):
                        if node.func.value.attr == "train":
                            if isinstance(node.func.value.value, ast.Name):
                                if node.func.value.value.id == "tf":
                                    if node.func.attr in tf_train_functions:
                                        name = f"{node.func.value.value.id}.{node.func.value.attr}.{node.func.attr}"
                                    #print(name)
                                
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id == "flags":
                            name = f"{node.func.value.id}.{node.func.attr}"
                        if node.func.value.id == "parser":
                            name = f"{node.func.value.id}.{node.func.attr}"

                        
                #elif isinstance(node.func, ast.Name):
                #    name = node.func.id
                        #print(ast.get_source_segment(codestr, node))
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
    
    """
    for index, row in old_collector.constants.iterrows():
        print(f'name: {row["name"]}, value: {row["value"]}')
    
    for index, row in new_collector.constants.iterrows():
        print(f'name: {row["name"]}, value: {row["value"]}')
    """
    return old_collector.constants, new_collector.constants, old_collector.names
    #collector.visit(new_tree)
    #return collector.old_constants, collector.new_constants

def compare(oldcalls, newcalls):
    diff = difflib.unified_diff(oldcalls["node"].tolist(), newcalls["node"].tolist(), fromfile='file1', tofile='file2', lineterm='', n=0)
    lines = list(diff)[2:]
    added = [line[1:] for line in lines if line[0] == '+']
    removed = [line[1:] for line in lines if line[0] == '-']
            #print("added")
            #print(added)
            #print("removed")
            #print(removed)
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
    

def training_infrastructure(df):
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
        old_calls = old_detector.calls
        new_calls = new_detector.calls
        #print(old_calls)
        istrue = compare(old_calls, new_calls)

        if istrue:
            count = count + 1
    if count>0:
        changes = True
    print(changes)
    return changes


if __name__ == "__main__":
    file = "https://github.com/google/youtube-8m/commit/53ba9e5279232cc51c5a7c8111e695c596992636"
    repo_path, commit_hash = clone_repo(file)
    df, analyze = commit_changes(repo_path, commit_hash)
    training_infrastructure(df)