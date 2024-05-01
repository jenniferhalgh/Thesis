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
                    if node.func.attr in ['write', 'savefig', 'to_csv', 'to_json', 'save_images']:
                        name = f"{node.func.attr}"
                    if isinstance(node.func.value, ast.Attribute):
                            if isinstance(node.func.value.value, ast.Name):
                                if node.func.value.attr == "summary" and node.func.value.value.id == "tf":
                                    if node.func.attr in ['audio', 'histogram', 'image', 'scalar', 'tensor_summary']:
                                        name = f"{node.func.value.value.id}.{node.func.value.attr}.{node.func.attr}"
                        
                    if isinstance(node.func.value, ast.Name):
                        #if node.func.value.id == "tf" and node.func.attr == "name_scope":
                        #    name = f"{node.func.value.id}.{node.func.attr}"
                        if node.func.value.id == "cv2" and node.func.attr == "imwrite":
                            name = f"{node.func.value.id}.{node.func.attr}"
                        if node.func.value.id == "metrics":
                            name = f"{node.func.value.id}.{node.func.attr}"
                       
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['write', 'savefig', 'to_csv', 'to_json', 'save_images']:
                        #print(node.func.id)
                        name = f"{node.func.id}"

                        
                #elif isinstance(node.func, ast.Name):
                #    name = node.func.id
                        #print(ast.get_source_segment(codestr, node))
                if name:
                    new_row = {'name': name, 'node': str(ast.dump(node))}
                    self.calls.loc[len(self.calls)] = new_row

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

def output_data(df):
    changes = False
    count = 0
    for index, row in df.iterrows():
        old_content = df["oldFileContent"].iloc[index]
        new_content = df["currentFileContent"].iloc[index]
        ast1 = ast.parse(old_content)
        ast2 = ast.parse(new_content)
        #detector = CodeChangeDetector(old_content, new_content)
        #detector.detect_changes()
        old_detector = CodeChangeDetector(old_content)
        new_detector = CodeChangeDetector(new_content)
        old_detector.find_Call(ast1)
        new_detector.find_Call(ast2)
        old_calls = old_detector.calls
        new_calls = new_detector.calls
        #print(old_calls)
        istrue = compare(old_calls, new_calls)

        if istrue:
            count = count + 1
        """
        if len(detector.changes)!=0:
            print(f"Changes detected in {df['Path'][index]}:")
            for change in detector.changes:
                print(f" - {change}")
            changes = True
        else:
            print(f"No specific 'output data type' changes detected in {df['Path'][index]}.")
            print("")
        """
    if count>0:
        changes = True
    print(changes)
    return changes

if __name__ == "__main__":
    
    #repo_url = "https://github.com/Mappy/tf-faster-rcnn"
    #commit_hash = "51e0889fbdcd4c48f31def4c1cb05a5a4db04671"
    #repo_url = "https://github.com/Mappy/tf-faster-rcnn"
    #commit_hash = "29aefedc73be3d7419ba72802f347e372382db7d"
    #repo_url = "https://github.com/thtrieu/darkflow"
    #commit_hash = "ea141f91e59e8b8da92e2292f00bb601e0e69008"
    #repo_url = "https://github.com/atriumlts/subpixel"
    #commit_hash = "0852d4b49d38f02cf2e699a63f6b5fec63ef7ea7"
    #repo_url = "https://github.com/jakeret/tf_unet"
    #commit_hash = "9f0e79b6a38c0bbb26d674d83851e18ca0f379cc"
    #repo_url = "https://github.com/google/youtube-8m"
    #commit_hash = "462baeeb1209e3add9ed728c4b0f9dd6dde9ba9b"
    #repo_url = "https://github.com/andrewb-ms/fast-style-transfer"
    #commit_hash = "47c993b71e2fe717e21fc3da4e8e69261832ca85"
    repo_path, commit_hash = clone_repo("https://github.com/EkaterinaPogodina/tf-faster-rcnn/commit/94879e12edefd6f7c0e006c798258f0bbe0818da#diff-86fa66d9ee46889e786fc4a2fa0ba0afe05ca08c00f81bf3d95ae3eeae426e5fR193")
    df, analyze = commit_changes(repo_path, commit_hash)
    #print(df)
    if analyze : 
        output_data(df)
    
