import argparse
from repo_utils import clone_repo
from repo_changes import commit_changes
"""
# Define the argument parser
parser = argparse.ArgumentParser(description='Clone GitHub repository.')
parser.add_argument('github_link', type=str, help='GitHub link containing username, repository name, and commit hash')

# Parse the arguments
args = parser.parse_args()
"""
# Call the clone_repo_args function with the parsed arguments
#repo_path, commit_hash = clone_repo("https://github.com/DeepLabCut/DeepLabCut/commit/6568c2ba6facf5d90b2c39af7b0f024a40f2b15f")
repo_path, commit_hash = clone_repo("https://github.com/MaybeShewill-CV/CRNN_Tensorflow/commit/2ca0efb80ea45f02719761e6673091dae8ae3e8c")
#repo_path, commit_hash = clone_repo("https://github.com/lancele/Semantic-Segmentation-Suite/commit/d50b5c812392614fc2bdaf269921beb1f7086f63")

commit_changes(repo_path, commit_hash)
