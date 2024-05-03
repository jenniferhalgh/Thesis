import os
from urllib.parse import urlparse
import pandas as pd
import ast
from git import Repo
import git
import numpy as np
from repo_utils import clone_repo
from sklearn.model_selection import train_test_split

def fix_url(downstream):
    df = pd.read_csv(downstream)
    for i in range(len(df["sample_url"])):
        parsed_url = urlparse(df["sample_url"][i])
        
        path_segments = parsed_url.path.strip('/').split('/')
        #print(path_segments)
        repos, username, repo_name, commits, commit_hash = path_segments
        correct_path = f"https://github.com/{username}/{repo_name}/commit/{commit_hash}"
        df["sample_url"][i] = correct_path
        df.to_csv("./repomanager/Data/downstream_processed.csv", index=False)
        #print(df.iloc[i, 0], df.iloc[i, 2])

def remove_unavailable_repos(file):
    if file == "upstream":
        file = "./repomanager/Data/Original Data/upstream_processed.csv"
        output_file = "./repomanager/Data/upstream_processed_new.csv"
    elif file == "downstream":
        file = "./repomanager/Data/Original Data/downstream_processed.csv"
        output_file = "./repomanager/Data/downstream_processed_new.csv"
    df = pd.read_csv(file)
    rows_to_drop = [] 
    for i in range(len(df["sample_url"])):
        link = df["sample_url"][i]
        a, b = clone_repo(link)
        if not a and not b:
            print("drop")
            rows_to_drop.append(i)
    
    print(rows_to_drop)
    df.drop(rows_to_drop, axis = 0, inplace=True)
    
    # Reset indices after dropping rows
    df.reset_index(drop=True, inplace=True)
    
    df.to_csv(output_file, index=False)

def check_filetype(repo_path, commit_hash=None):
    drop_row = False
    repo = Repo(repo_path)
    if commit_hash:
        try:
            commit = repo.commit(commit_hash)
        except ValueError as ve:
            print(f"ValueError occurred: {ve}")
            return drop_row
    count = 0
    for item in commit.diff(commit.parents[0]).iter_change_type('M'):

        #print("hello")
        path = item.a_path
        
        if not path.endswith('.py') and not path.endswith('.cfg'):
            count = count + 1
            
    if not count > 0:
        drop_row = True
    
    return drop_row


def drop_nonpy_rows(file):
    if file == "upstream":
        file = "./repomanager/Data/upstream_processed_new.csv"
        output_file = "./repomanager/Data/upstream_processed_new.csv"
    elif file == "downstream":
        file = "./repomanager/Data/downstream_processed_new.csv"
        output_file = "./repomanager/Data/downstream_processed_new.csv"
    df = pd.read_csv(file)
    rows_to_drop = [] 
    drop = False
    for i in range(len(df["sample_url"])):
        
        link = df["sample_url"][i]
        print(link)
        repo_path, commit_hash = clone_repo(link)
        drop = check_filetype(repo_path, commit_hash)
        if drop:
            rows_to_drop.append(i)
    
    df.drop(rows_to_drop, axis = 0, inplace=True)
    
    # Reset indices after dropping rows
    df.reset_index(drop=True, inplace=True)
    
    df.to_csv(output_file, index=False)

def extract_data(file_path):
    df = pd.read_csv(file_path)
    for c in df.columns:
        if c!="Index" and c!="sample_url":
            non_empty_rows = df[df[c].notna()]
            dir = f"./repomanager/Data/Columns"
            output_file_path = f"{dir}/{c}.csv"
            non_empty_rows.to_csv(output_file_path, index=False)

def get_columns(file):
    if file == "upstream":
        file_path = "./repomanager/Data/upstream_processed_new.csv"
        output_file = "./repomanager/Data/upstream_processed_new.csv"
    elif file == "downstream":
        file_path = "./repomanager/Data/downstream_processed_new.csv"
        output_file = "./repomanager/Data/downstream_processed_new.csv"
    df = pd.read_csv(file_path)
    for c in df.columns:
        extract_data(file, file_path, c)

#Split the dataset (70% training and 30% testing), file is a string ("upstream" or "downstream")
def split_ML(test_size=0.3, random_state=39):
    dir = "./repomanager/Data/Columns"
    ML_changes = ['program data', 'input data', 'output data', 'preprocessing', 'param tinkering', 'evaluation_code_change', 'performance', 'training chng', 'model chng']
    for file in os.listdir(dir):
        file_path = os.path.join(dir, file)
        column = file.rsplit(".", 1)[0]
        if column in ML_changes:
            print(column)
            df = pd.read_csv(file_path)
            train, test = train_test_split(df, test_size=test_size, random_state=random_state)
            train.to_csv(f"./repomanager/Data/training/{column}.csv", index = False)
            test.to_csv(f"./repomanager/Data/testing/{column}.csv", index = False)

def split_non_ML(test_size=0.3, random_state=42):
    dfs = []
    dir = "./repomanager/Data/Columns"
    ML_changes = ['program data', 'input data', 'output data', 'preprocessing', 'param tinkering', 'evaluation_code_change', 'performance', 'training chng', 'model chng']
    for file in os.listdir(dir):
        file_path = os.path.join(dir, file)
        column = file.rsplit(".", 1)[0]
        if column not in ML_changes:
            df = pd.read_csv(file_path)
            dfs.append(df)
            print(column)
            
    combined_dataset = pd.concat(dfs, axis=0)
    combined_dataset.drop_duplicates(inplace=True)
    train, test = train_test_split(combined_dataset, test_size=test_size, random_state=random_state)
    train.to_csv(f"./repomanager/Data/training/training_nonML.csv", index = False)
    test.to_csv(f"./repomanager/Data/testing/testing_nonML.csv", index = False)

def combine_dataset():
    upstream = pd.read_csv("./repomanager/Data/upstream_processed_new.csv")
    downstream = pd.read_csv("./repomanager/Data/downstream_processed_new.csv")
    all_columns = set(upstream.columns) | set(downstream.columns)
    columns_to_drop = []
    #add_missing_columns(upstream, all_columns - set(upstream.columns))
    
    #add_missing_columns(downstream, all_columns - set(downstream.columns))
    combined_dataset = pd.concat([upstream, downstream], axis=0)
    for c in combined_dataset.columns:
        if "deprecated" in str(c) or "Deprecated" in str(c):
            columns_to_drop.append(c)
    
    combined_dataset.drop(columns=columns_to_drop, inplace=True)
    #combined_dataset = pd.merge(upstream, downstream, how='outer', on=list(all_columns))
    print(combined_dataset.columns)
    combined_dataset.to_csv("./repomanager/Data/dataset.csv", index=False)

def remove_empty_rows():
    dataset = pd.read_csv("./repomanager/Data/dataset.csv")
    columns_to_check = dataset.columns.difference(['Index', 'sample_url'])
    rows_to_drop = []
    for index, row in dataset.iterrows():
        if row[columns_to_check].isnull().all():  # Check if all specified columns are NaN (empty)
            rows_to_drop.append(index)
    print(rows_to_drop)
    dataset.drop(rows_to_drop, inplace=True)  # Drop the row
    dataset.to_csv("./repomanager/Data/dataset.csv", index=False)


def filter(file1):
    dir = f"./repomanager/Data/{file1}"
    data = []
    for file in os.listdir(dir):
        file_path = os.path.join(dir, file)
        df = pd.read_csv(file_path)
        data.append(df)
    
    combined_dataset = pd.concat(data, axis=0)
    combined_dataset.drop_duplicates(inplace=True)
    combined_dataset.to_csv(f"./repomanager/Data/{file1}/{file1}_ML.csv", index = False)

def find_index(urls, df):
    indices = []
    for index, row in df.iterrows():
        if df["sample_url"][index] in urls.tolist():
            indices.append(index)
    return indices

def check_overlapping_rows():
    train = pd.read_csv("./repomanager/Data/training_set.csv")
    df11 = train["sample_url"]
    test = pd.read_csv("./repomanager/Data/testing_set.csv")
    df22 = test["sample_url"]
    
    # Merge the DataFrames on all columns
    merged_df = pd.merge(df11, df22, how='inner', on='sample_url')
    
    # Check if there are any overlapping rows
    if not merged_df.empty:
        print("There are overlapping rows between the DataFrames.")
        # Optionally, you can print or return the overlapping rows
        print(merged_df["sample_url"])
        seventy, thirty = train_test_split(merged_df["sample_url"], test_size=0.3, random_state=123)
        print(seventy)
        print(thirty)

        train_drop = find_index(seventy, train)
        test_drop = find_index(thirty, test)
        
        train.drop(train_drop, inplace=True)  # Drop the row
        test.drop(test_drop, inplace=True)  # Drop the row

        train.to_csv("./repomanager/Data/training_set.csv", index=False)
        test.to_csv("./repomanager/Data/testing_set.csv", index=False)

    else:
        print("There are no overlapping rows between the DataFrames.")


if __name__ == "__main__":
    upstream = "./repomanager/Data/Original Data/upstream_processed.csv"
    downstream = "./repomanager/Data/Original Data/downstream_processed.csv"
    dataset = "./repomanager/Data/dataset.csv"
    #remove_unavailable_repos("upstream")
    #remove_unavailable_repos("downstream")
    #combine_dataset()
    #remove_empty_rows()
    #extract_data(dataset)


    #drop_nonpy_rows("upstream")
    #drop_nonpy_rows("downstream")
    #list_columns()
    
    #split_ML()
    #split_non_ML()
    #filter("training")
    #filter("testing")
    #check_overlapping_rows()

    #commit_changes("upstream")
    #split("downstream")
    #get_columns("downstream")
    """
    training1 = pd.read_csv("./repomanager/Data/training/training_ML.csv")
    training2 = pd.read_csv("./repomanager/Data/training/training_nonML.csv")
    testing1 = pd.read_csv("./repomanager/Data/testing/testing_ML.csv")
    testing2 = pd.read_csv("./repomanager/Data/testing/testing_nonML.csv")
    training_dataset = pd.concat([training1, training2], axis=0)
    testing_dataset = pd.concat([testing1, testing2], axis=0)
    training_dataset.drop_duplicates(inplace=True)
    testing_dataset.drop_duplicates(inplace=True)
    training_dataset.to_csv(f"./repomanager/Data/training_set.csv", index = False)
    testing_dataset.to_csv(f"./repomanager/Data/testing_set.csv", index = False)
    """
    #check_overlapping_rows()


