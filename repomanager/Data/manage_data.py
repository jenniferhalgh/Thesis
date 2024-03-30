import os
import pandas as pd
from sklearn.model_selection import train_test_split

def extract_data(file, category):
    file_path = f"./repomanager/Data/{file}_processed.csv"
    df = pd.read_csv(file_path)

    non_nan_rows = df[df[category].notna()]
    dir = f"./repomanager/Data/Categories/{category}"
    output_file_path = f"{dir}/{file}_{category}.csv"
    if not os.path.exists(dir):
        os.makedirs(dir)
    non_nan_rows.to_csv(output_file_path, index=False)

def split_data(upstream, downstream, test_size=0.3, random_state=123):
    up_df = pd.read_csv(upstream)
    down_df = pd.read_csv(downstream)
    up_train, up_test = train_test_split(up_df, test_size=test_size, random_state=random_state)
    down_train, down_test = train_test_split(down_df, test_size=test_size, random_state=random_state)
    #combined_train = pd.concat([up_train, down_train])
    #combined_test = pd.concat([up_test, down_test])
    return up_train, up_test, down_train, down_test


#extract_data("upstream", "param tinkering")
#extract_data("downstream", "param tinkering")
up_train, up_test, down_train, down_test = split_data("./repomanager/Data/Categories/input data/upstream_input data.csv", "./repomanager/Data/Categories/input data/downstream_input data.csv")
up_train.to_csv("./repomanager/Data/training/input data_up.csv")
down_train.to_csv("./repomanager/Data/training/input data_down.csv")
up_test.to_csv("./repomanager/Data/testing/input data_up.csv")
down_test.to_csv("./repomanager/Data/testing/input data_down.csv")
