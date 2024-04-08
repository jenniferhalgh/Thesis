import os
import pandas as pd
from sklearn.model_selection import train_test_split
from urllib.parse import urlparse

from repo_utils import clone_repo

def extract_data(file, category):
    file_path = f"./repomanager/Data/{file}_processed.csv"
    df = pd.read_csv(file_path)

    empty_rows = df[df[category].notna()]
    dir = f"./repomanager/Data/Categories/{category}"
    output_file_path = f"{dir}/{file}_{category}.csv"
    if not os.path.exists(dir):
        os.makedirs(dir)
    empty_rows.to_csv(output_file_path, index=False)

def split_data(upstream, downstream, test_size=0.3, random_state=123):
    up_df = pd.read_csv(upstream)
    down_df = pd.read_csv(downstream)
    up_train, up_test = train_test_split(up_df, test_size=test_size, random_state=random_state)
    down_train, down_test = train_test_split(down_df, test_size=test_size, random_state=random_state)
    #combined_train = pd.concat([up_train, down_train])
    #combined_test = pd.concat([up_test, down_test])
    return up_train, up_test, down_train, down_test

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

def preprocess(file):
    df = pd.read_csv(file)
    rows_to_drop = [] 
    for i in range(len(df["sample_url"])):
        link = df["sample_url"][i]
        a, b = clone_repo(link)
        if not a and not b:
            print("drop")
            rows_to_drop.append(i)
    
    df.drop(rows_to_drop, inplace=True)
    
    # Reset indices after dropping rows
    df.reset_index(drop=True, inplace=True)

    df.to_csv(file, index=False)


#preprocess("./repomanager/Data/upstream_processed.csv")


#choose category here
category = "model chng"
extract_data("upstream", category)
extract_data("downstream", category)

filepath = "./repomanager/Data/Categories"
up_train, up_test, down_train, down_test = split_data(f"{filepath}/{category}/upstream_{category}.csv", f"{filepath}/{category}/downstream_{category}.csv")
up_train.to_csv(f"./repomanager/Data/training/{category}_up.csv", index = False)
down_train.to_csv(f"./repomanager/Data/training/{category}_down.csv", index = False)
up_test.to_csv(f"./repomanager/Data/testing/{category}_up.csv", index = False)
down_test.to_csv(f"./repomanager/Data/testing/{category}_down.csv", index = False)

"""
df = pd.read_csv("./repomanager/Data/upstream_processed.csv")
df['sample url'] = df["Unnamed: 2"]
df = df.drop('Unnamed: 2', axis=1)
df.to_csv("./repomanager/Data/upstream_processed.csv", index=False)

df = pd.read_csv("./repomanager/Data/upstream_processed.csv")
df.rename(columns = {'sample url':'sample_url'}, inplace = True) 
df.to_csv("./repomanager/Data/upstream_processed.csv", index=False)
"""