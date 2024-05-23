import argparse
from urllib.parse import urlparse
from repo_utils import clone_repo
from repo_changes import commit_changes
from parameter_tuning_2 import parameter_tuning
from output_data_2 import output_data
from training_infrastructure import training_infrastructure
from model_structure import model_structure
from input_data import input_data
import numpy as np
import pandas as pd
import os

def evaluate_one(link):
    repo_path, commit_hash = clone_repo(link)
    df = commit_changes(repo_path, commit_hash)

def evaluate_all():
    df = pd.read_csv("testing_dataset")

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
                repo_path, commit_hash, username, repo_name = clone_repo(df["sample_url"][index])
                parsed_url = urlparse(df["sample_url"][index])
                path_segments = parsed_url.path.strip('/').split('/')
                
                username, repo_name, commit, commit_hash = path_segments
                #print(repo_path)
                print(df["sample_url"][index])
                if df["sample_url"][index] not in urls:
                    urls.add(df["sample_url"][index])
                    if repo_path and commit_hash:
                        commit, analyze = commit_changes(repo_path, commit_hash, username, repo_name)
                        if analyze:
                            if category == "param tinkering":
                                change = parameter_tuning(commit)
                            elif category == "output data":
                                change = output_data(commit)
                            elif category == "model chng":
                                change = model_structure(commit)
                            elif category == "input data":
                                change = input_data(commit)
                            elif category == "training chng":
                                change = training_infrastructure(commit)

                            #predicted pt
                            if change:
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
                            elif not change:
                                #actual not pt
                                if not pd.notna(df[category][index]):
                                    true_n = true_n + 1
                                    print("True negative")
                                #acual pt
                                else:
                                    false_n = false_n + 1
                                    print("False negative")
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
    print(f"unavailable (due to no .py file): {unavailable}")
    confusion_matrix.to_csv(f"./repomanager/cm-{category}.csv")
                    
    
            

if __name__ == "__main__":
    #test_data("param tinkering")
    #confusion_matrix("param tinkering")

    test_data("output data")
    #confusion_matrix("output data")

    #test_data("training chng")
    #confusion_matrix("training chng")

    #test_data("model chng")
    #confusion_matrix("model chng")

    #test_data("input data")
    #confusion_matrix("input data")