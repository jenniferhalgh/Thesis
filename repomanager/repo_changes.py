import ast
import os
import pandas as pd
from git import Repo
import git


def commit_changes(repo_path, commit_hash=None):
    modified_files = []
    repo = Repo(repo_path)
    if commit_hash:
        try:
            commit = repo.commit(commit_hash)
        except ValueError as e:
            print(e)
            return pd.DataFrame()
    df = pd.DataFrame()

    for item in commit.diff(commit.parents[0]).iter_change_type('M'):
        #print("hello")
        path = item.a_path

        if not path.endswith('.py') and not path.endswith('.cfg'):
            df = pd.DataFrame(modified_files)
            df.to_csv("pt.csv", index=False)
            print("break")
            return df

    for item in commit.diff(commit.parents[0]).iter_change_type('M'):
        #print("hello")
        path = item.a_path

        if not path.endswith('.py') and not path.endswith('.cfg'):
            df = pd.DataFrame(modified_files)
            df.to_csv("pt.csv", index=False)
            print("break")
            return df
        
        if path.endswith('.py') or path.endswith('.cfg'):
            try:
                old_file_content = ast.dump(ast.parse(repo.git.show(f'{commit.parents[0]}:{path}')))
                current_file_content = ast.dump(ast.parse(repo.git.show(f'{commit.hexsha}:{path}')))
                modified_files.append(
                {"Path": path, "oldFileContent": old_file_content, "currentFileContent": current_file_content})
            except SyntaxError as e:
                print(f"SyntaxError occurred while parsing file {path}: {e}")
            except git.exc.GitCommandError as ge:
                print(ge)
            except ValueError as e:
                df = pd.DataFrame(modified_files)
                df.to_csv("pt.csv", index=False)
                return df
    df = pd.DataFrame(modified_files)
    df.to_csv("pt.csv", index=False)
    return df