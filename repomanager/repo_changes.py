import ast
import os
import pandas as pd
from git import Repo
import git

"""
This code is based on the code in https://github.com/PyRef/PyRef/tree/main.
H. Atwi, B. Lin, N. Tsantalis, Y. Kashiwa, Y. Kamei, N. Ubayashi, G. Bavota and M. Lanza, "PyRef: Refactoring Detection in Python Projects," 2021 IEEE 21st International Working Conference on Source Code Analysis and Manipulation (SCAM), 2021, accepted.
"""

def commit_changes(repo_path, commit_hash=None):
    modified_files = []
    repo = Repo(repo_path)
    if commit_hash:
        try:
            commit = repo.commit(commit_hash)
        except ValueError as e:
            print(e)
            return pd.DataFrame(), True
    df = pd.DataFrame()
    
    for item in commit.diff(commit.parents[0]).iter_change_type('A'):
        path = item.a_path
        if not path.endswith('.py'):
            df = pd.DataFrame(modified_files)
            df.to_csv("pt.csv", index=False)
            print("non-python")
            return df, False
    for item in commit.diff(commit.parents[0]).iter_change_type('D'):
        path = item.a_path
        if not path.endswith('.py'):
            df = pd.DataFrame(modified_files)
            df.to_csv("pt.csv", index=False)
            print("non-python")
            return df, False
    
    for item in commit.diff(commit.parents[0]).iter_change_type('M'):
        path = item.a_path
        if not path.endswith('.py'):
            df = pd.DataFrame(modified_files)
            df.to_csv("pt.csv", index=False)
            print("non-python")
            return df, False
    
    

    for item in commit.diff(commit.parents[0]).iter_change_type('M'):
        #print("hello")
        path = item.a_path
        
        if path.endswith('.py'):
            try:
                old_file_content = repo.git.show(f'{commit.parents[0]}:{path}')
                current_file_content = repo.git.show(f'{commit.hexsha}:{path}')
                ast1 = ast.parse(old_file_content)
                ast2 = ast.parse(current_file_content)
                modified_files.append(
                {"Path": path, "oldFileContent": old_file_content, "currentFileContent": current_file_content})
            except SyntaxError as e:
                print(f"SyntaxError occurred while parsing file {path}: {e} (pyhton 2)")
                df = pd.DataFrame()
                return df, False
            except git.exc.GitCommandError as ge:
                print(ge)
            except ValueError as e:
                df = pd.DataFrame(modified_files)
                
                return df, True
    df = pd.DataFrame(modified_files)
    return df, True