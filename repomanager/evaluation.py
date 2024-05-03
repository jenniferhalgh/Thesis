import argparse
from urllib.parse import urlparse
from repo_utils import clone_repo
from repo_changes import commit_changes
from parameter_tuning_copy import parameter_tuning
from output_data_copy import output_data
from training_infrastructure import training_infrastructure
from model_structure import model_structure
from input_data import input_data
import numpy as np
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

"""
def confusion_matrix():
    confusion_matrix = pd.DataFrame()
    #confusion_matrix[""] = np.nan
    categories = []
    file = './repomanager/Data/testing_set.csv'
    df = pd.read_csv(file)
    for c in df.columns:
        if c != "sample_url" and c != "Index":
            confusion_matrix[c] = pd.Series([0] * 48)
    print(len(confusion_matrix.columns))
    index_ = confusion_matrix.columns
  
    # Set the index 
    confusion_matrix.index = index_ 
    confusion_matrix.to_csv("./repomanager/cm.csv")
"""    
def confusion_matrix(category):
    cm = pd.DataFrame()
    cm[f"(p) - {category}"] = pd.Series([0] * 2)
    cm[f"(p) - not {category}"] = pd.Series([0] * 2)
    indices = [f"(a) - {category}", f"(a) - not {category}"]
    index_ = indices
    cm.index = index_ 
    cm.to_csv(f"./repomanager/cm-{category}.csv")
    return cm


def test_data(category):
    #df = confusion_matrix(category)
    true_p = 0
    false_p = 0
    false_n = 0
    true_n = 0
    pt = False
    count = 0
    count_output = 0
    unavailable = 0
    urls = set()
    test_data = pd.DataFrame()
    confusion_matrix = pd.read_csv(f"./repomanager/cm-{category}.csv", index_col=0)
    #print(confusion_matrix.columns)
    index_names = confusion_matrix.index.tolist()
    #print(index_names)
    directory = './repomanager/Data/test_pt'
    # Iterate over files in the directory
    for folder in os.listdir(directory):
        folder_path = os.path.join(directory, folder)
        for file in os.listdir(folder_path):
            filepath = os.path.join(folder_path, file)
            parts = file.rsplit(".", 1)
            df = pd.read_csv(filepath)
            for index, row in df.iterrows():
                repo_path, commit_hash = clone_repo(df["sample_url"][index])
                parsed_url = urlparse(df["sample_url"][index])
                path_segments = parsed_url.path.strip('/').split('/')
                
                username, repo_name, commit, commit_hash = path_segments
                #print(repo_path)
                print(df["sample_url"][index])
                if df["sample_url"][index] not in urls:
                    urls.add(df["sample_url"][index])
                    if repo_path and commit_hash:
                        commit, analyze = commit_changes(repo_path, commit_hash)
                        if analyze:
                            if category == "param tinkering":
                                pt = parameter_tuning(commit)
                                #od = output_data(commit)

                                #predicted pt
                                if pt:
                                    #actual pt
                                    if pd.notna(df[category][index]):
                                        #true positive
                                        true_p = true_p + 1 
                                        print("True positive")
                                    #actual not pt
                                    else:
                                        #false positive
                                        false_p = false_p + 1
                                        print(f"False positive")
                                    count = count + 1
                                #predicted not pt
                                elif not pt:
                                    #actual not pt
                                    if not pd.notna(df[category][index]):
                                        true_n = true_n + 1
                                        print("True negative")
                                    #acual pt
                                    else:
                                        false_n = false_n + 1
                                        print("False negative")
                            elif category == "output data":
                                #pt = parameter_tuning(commit)
                                od = output_data(commit)

                                #predicted pt
                                if od:
                                    #actual pt
                                    if pd.notna(df[category][index]):
                                        #true positive
                                        true_p = true_p + 1 
                                        print("True positive")
                                    #actual not pt
                                    else:
                                        #false positive
                                        false_p = false_p + 1
                                        print(f"False positive")
                                    count_output = count_output + 1
                                #predicted not pt
                                elif not pt:
                                    #actual not pt
                                    if not pd.notna(df[category][index]):
                                        true_n = true_n + 1
                                    #acual pt
                                    else:
                                        print("False negative")
                                        false_n = false_n + 1

                            elif category == "model chng":
                                #pt = parameter_tuning(commit)
                                ti = model_structure(commit)

                                #predicted pt
                                if ti:
                                    #actual pt
                                    if pd.notna(df[category][index]):
                                        #true positive
                                        true_p = true_p + 1 
                                        print("True positive")
                                    #actual not pt
                                    else:
                                        #false positive
                                        false_p = false_p + 1
                                        print(f"False positive")
                                    count_output = count_output + 1
                                #predicted not pt
                                elif not ti:
                                    #actual not pt
                                    if not pd.notna(df[category][index]):
                                        true_n = true_n + 1
                                    #acual pt
                                    else:
                                        print("False negative")
                                        false_n = false_n + 1

                            elif category == "input data":
                                #pt = parameter_tuning(commit)
                                inda = input_data(commit)

                                #predicted pt
                                if inda:
                                    #actual pt
                                    if pd.notna(df[category][index]):
                                        #true positive
                                        true_p = true_p + 1 
                                        print("True positive")
                                    #actual not pt
                                    else:
                                        #false positive
                                        false_p = false_p + 1
                                        print(f"False positive")
                                    #count_output = count_output + 1
                                #predicted not pt
                                elif not inda:
                                    #actual not pt
                                    if not pd.notna(df[category][index]):
                                        true_n = true_n + 1
                                    #acual pt
                                    else:
                                        print("False negative")
                                        false_n = false_n + 1
                            
                                
                                #confusion_matrix.at['param tinkering', parts[0]] = confusion_matrix.at['param tinkering', parts[0]] + 1
                            #if od:
                            #   count_output = count_output + 1
                        else:
                            print("unavailable")
                            unavailable = unavailable + 1
                    else:
                        unavailable = unavailable + 1
        
    confusion_matrix.iloc[0, 0] = true_p
    confusion_matrix.iloc[0, 1] = false_n
    confusion_matrix.iloc[1, 0] = false_p
    confusion_matrix.iloc[1, 1] = true_n
    print(f"true p: {true_p}")
    print(f"false p: {false_p}")
    print(f"true n: {true_n}")
    print(f"false n: {false_n}")
    print(f"pt: {count}")
    print(f"output data: {count_output}")
        #print(f"accuracy: {count}")
    print(f"unavailable (due to no .py file): {unavailable}")
    confusion_matrix.to_csv(f"./repomanager/cm-{category}.csv")
                    
    
            

if __name__ == "__main__":
    #test_data("param tinkering")
    #confusion_matrix("param tinkering")

    #test_data("output data")
    #confusion_matrix("output data")

    #test_data("training chng")
    #confusion_matrix("training chng")

    #test_data("model chng")
    #confusion_matrix("model chng")

    test_data("input data")
    #confusion_matrix("input data")