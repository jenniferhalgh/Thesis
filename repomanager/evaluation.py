import argparse
from repo_utils import clone_repo
from repo_changes import commit_changes
from parameter_tuning import parameter_tuning
#from find_change2 import param_tuning
import pandas as pd
import os
"""
# Define the argument parser
parser = argparse.ArgumentParser(description='Clone GitHub repository.')
parser.add_argument('github_link', type=str, help='GitHub link containing username, repository name, and commit hash')

# Parse the arguments
args = parser.parse_args()
"""
# Call the clone_repo_args function with the parsed arguments
#repo_path, commit_hash = clone_repo("https://github.com/DeepLabCut/DeepLabCut/commit/6568c2ba6facf5d90b2c39af7b0f024a40f2b15f")
repo_path, commit_hash = clone_repo("https://github.com/google/youtube-8m/commit/53ba9e5279232cc51c5a7c8111e695c596992636")
#repo_path, commit_hash = clone_repo("https://github.com/lancele/Semantic-Segmentation-Suite/commit/d50b5c812392614fc2bdaf269921beb1f7086f63")


def evaluate_one(link):
    repo_path, commit_hash = clone_repo(link)
    df = commit_changes(repo_path, commit_hash)
    #param_tuning(df)

def evaluate_all():
    df = pd.read_csv("testing_dataset")

def test_data():
    pt = False
    count = 0
    unavailable = 0
    test_data = pd.DataFrame()
    directory = './repomanager/Data/testing/test_pt'
    # Iterate over files in the directory
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        df = pd.read_csv(filepath)
        for index, row in df.iterrows():
            repo_path, commit_hash = clone_repo(df["sample_url"][index])
            print(df["sample_url"][index])
            if repo_path and commit_hash:
                commit = commit_changes(repo_path, commit_hash)
                if not commit.empty:
                    pt = parameter_tuning()
                    if pt:
                        #print("True")
                        count = count + 1
                else:
                    unavailable = unavailable + 1
            else:
                unavailable = unavailable + 1
    
    print(f"parameter tuning: {count}")
    #print(f"accuracy: {count}")
    print(f"unavailable (due to no .py file): {unavailable}")
                
    
            

if __name__ == "__main__":
    test_data()