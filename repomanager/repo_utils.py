import os
import git
from git import Repo
from os import path
from urllib.parse import urlparse

"""
This code is based on the code in https://github.com/PyRef/PyRef/tree/main.
H. Atwi, B. Lin, N. Tsantalis, Y. Kashiwa, Y. Kamei, N. Ubayashi, G. Bavota and M. Lanza, "PyRef: Refactoring Detection in Python Projects," 2021 IEEE 21st International Working Conference on Source Code Analysis and Manipulation (SCAM), 2021, accepted.
"""



def clone_repo(github_link):
    parsed_url = urlparse(github_link)
    if parsed_url.scheme != 'https' or parsed_url.netloc != 'github.com':
        print("Invalid GitHub link.")
        print(parsed_url.scheme)
        return None

    path_segments = parsed_url.path.strip('/').split('/')
    if len(path_segments) != 4:
        print(path_segments)
        print("Invalid GitHub link format.")
        return None

    username, repo_name, commit, commit_hash = path_segments
    
    git_url = f'https://github.com/{username}/{repo_name}.git'
    repo_path = os.path.abspath(f"./Repos/{username}/{repo_name}")
    if path.exists(repo_path):
        #print("Repo Already Cloned.")
        return repo_path, commit_hash

    try:
        print("Cloning Repo...")
        repo = Repo.clone_from(git_url, repo_path, branch='main', no_checkout=True, mirror=True)
        
        return repo_path, commit_hash
    except git.exc.GitCommandError as e:
        if 'Repository not found' in str(e):
            print("none")
            return None, None
        else:
            try:
                repo = Repo.clone_from(git_url, repo_path, branch='master', no_checkout=True, mirror=True)
            except git.exc.GitCommandError as e:
                repo = Repo.clone_from(git_url, repo_path, no_checkout=True, mirror=True)
    
        return repo_path, commit_hash

