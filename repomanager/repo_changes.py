import ast
import os
import pandas as pd
from git import Repo


def commit_changes(repo_path, commit_hash=None):
    modified_files = []
    repo = Repo(repo_path)
    if commit_hash:
        commit = repo.commit(commit_hash)
    df = pd.DataFrame()
    for item in commit.diff(commit.parents[0]).iter_change_type('M'):
        #print("hello")
        path = item.a_path
        
        if path.endswith('.py') or path.endswith('.cfg'):
            try:
                old_file_content = ast.dump(ast.parse(repo.git.show(f'{commit.parents[0]}:{path}')))
                current_file_content = ast.dump(ast.parse(repo.git.show(f'{commit.hexsha}:{path}')))
                modified_files.append(
                {"Path": path, "oldFileContent": old_file_content, "currentFileContent": current_file_content})
            except SyntaxError as e:
                print(e)
    df = pd.DataFrame(modified_files)
    df.to_csv("pt.csv", index=False)
    return df