import ast
import os
import requests
import pandas as pd
from git import Repo
import git
import json
import pprint
import base64

"""
This code is based on the code in https://github.com/PyRef/PyRef/tree/main.
H. Atwi, B. Lin, N. Tsantalis, Y. Kashiwa, Y. Kamei, N. Ubayashi, G. Bavota and M. Lanza, "PyRef: Refactoring Detection in Python Projects," 2021 IEEE 21st International Working Conference on Source Code Analysis and Manipulation (SCAM), 2021, accepted.
"""


def commit2(username, repo_name, commit_hash):
    modified_files = []
    df = pd.DataFrame()
    api_endpoint = f'https://api.github.com/repos/{username}/{repo_name}/commits/{commit_hash}'
    response = requests.get(api_endpoint)
    if response.status_code == 200:
        current_content = json.loads(response.text)
        #pprint.pprint(current_content)
        api_endpoint = current_content["parents"][0]["url"]
        #print(current_content["parents"][0]["url"])
        response = requests.get(api_endpoint)
        if response.status_code == 200:
            old_content = json.loads(response.text)
            #pprint.pprint(old_content)
            commit_sha = old_content["sha"]


        for file in current_content["files"]:
            api_endpoint = file["raw_url"]
            file_path = file["filename"]
            status = file["status"]

            if not file_path.endswith('.py'):
                df = pd.DataFrame(modified_files)
                print("non-python")
                return df, False

            if status == "modified" or status == "added":
                response = requests.get(api_endpoint)
                if response.status_code == 200:
                    current_file_content = response.text
            else:
                current_file_content = ""

            if status == "deleted":
                response = requests.get(f"https://api.github.com/repos/{username}/{repo_name}/contents/{file_path}?ref={commit_sha}")
                if response.status_code == 200:
                    data = json.loads(response.text)
                    content = data["content"]
                    encoding = data["encoding"]
                    if encoding == 'base64':
                        old_file_content = base64.b64decode(content).decode()
            else:
                old_file_content = ""
            
            try:
                
                ast1 = ast.parse(old_file_content)
                ast2 = ast.parse(current_file_content)

                modified_files.append(
                {"Path": file_path, "oldFileContent": old_file_content, "currentFileContent": current_file_content})
            except SyntaxError as e:
                print(f"SyntaxError occurred while parsing file {file_path}: {e} (pyhton 2)")
                df = pd.DataFrame()
                return df, False
            except git.exc.GitCommandError as ge:
                print("added")
                print(ge)
            except ValueError as e:
                break
    
    df = pd.DataFrame(modified_files)
    return df, True
        
  


def commit_changes(repo_path, commit_hash, username, repo_name):
    modified_files = []
    repo = Repo(repo_path)
    files = []
    if commit_hash:
        try:
            commit = repo.commit(commit_hash)
        except ValueError as e:
            return commit2(username, repo_name, commit_hash)
   
    df = pd.DataFrame()

    added = [diff for diff in commit.diff(commit.parents[0]).iter_change_type('A')]
    deleted = [diff for diff in commit.diff(commit.parents[0]).iter_change_type('D')]
    updated = [diff for diff in commit.diff(commit.parents[0]).iter_change_type('M')]
    
    for item in added:
        path = item.a_path
        if not path.endswith('.py'):
            df = pd.DataFrame(modified_files)
            df.to_csv("pt.csv", index=False)
            print("non-python")
            return df, False
        elif path.endswith('.py'):
            try:
                old_file_content = repo.git.show(f'{commit.parents[0]}:{path}')
                current_file_content = ""
                ast1 = ast.parse(old_file_content)
                ast2 = ast.parse(current_file_content)
                modified_files.append(
                {"Path": path, "oldFileContent": old_file_content, "currentFileContent": current_file_content})
            except SyntaxError as e:
                print(f"SyntaxError occurred while parsing file {path}: {e} (pyhton 2)")
                df = pd.DataFrame()
                return df, False
            except git.exc.GitCommandError as ge:
                print("added")
                print(ge)
            except ValueError as e:
                break


    for item in deleted:
        path = item.a_path
        if not path.endswith('.py'):
            df = pd.DataFrame(modified_files)
            df.to_csv("pt.csv", index=False)
            print("non-python")
            return df, False
        elif path.endswith('.py'):
            try:
                #old_file_content = repo.git.show(f'{commit.parents[0]}:{path}')
                current_file_content = repo.git.show(f'{commit.hexsha}:{path}')
                old_file_content = ""
                ast1 = ast.parse(old_file_content)
                ast2 = ast.parse(current_file_content)

                modified_files.append(
                {"Path": path, "oldFileContent": old_file_content, "currentFileContent": current_file_content})
            except SyntaxError as e:
                print(f"SyntaxError occurred while parsing file {path}: {e} (pyhton 2)")
                df = pd.DataFrame()
                return df, False
            except git.exc.GitCommandError as ge:
                if 'fatal: path' in ge.stderr and 'does not exist' in ge.stderr:
                    print("deleted")
                    print(f"Error: {path} does not exist in commit {commit.hexsha}")

                else:
                    print("deleted 2")
                    print(ge)
            except ValueError as e:
                break
    
    
    for item in updated:
        path = item.a_path
        if not path.endswith('.py'):
            df = pd.DataFrame(modified_files)
            df.to_csv("pt.csv", index=False)
            print("non-python")
            return df, False
        elif path.endswith('.py'):
            try:
                old_file_content = repo.git.show(f'{commit.parents[0]}:{item.b_path}')
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
                if 'fatal: path' in ge.stderr and 'does not exist' in ge.stderr:
                    old_file_content = repo.git.show(f'{commit.parents[0]}:{path}')
                    current_file_content = repo.git.show(f'{commit.hexsha}:{path}')
                    ast1 = ast.parse(old_file_content)
                    ast2 = ast.parse(current_file_content)
                    modified_files.append(
                        {"Path": path, "oldFileContent": old_file_content, "currentFileContent": current_file_content})
                    print("deleted")
                    print(f"Error: {path} does not exist in commit {commit.hexsha}")
                print("updated")
                print(ge)
            except ValueError as e:
                break
    df = pd.DataFrame(modified_files)
    return df, True