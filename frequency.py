import pandas as pd

def count_non_empty_rows():
    df1 = pd.read_csv("./repomanager/Data/Original Data/upstream_processed.csv")
    df2 = pd.read_csv("./repomanager/Data/Original Data/downstream_processed.csv")
    dfs = []
    dfs.append(df1)
    dfs.append(df2)
    combined_dataset = pd.concat(dfs, axis=0)
    combined_dataset.drop_duplicates(inplace=True)
    
    for c in combined_dataset.columns:
        if c!="Index" and c!="sample_url":
            count = combined_dataset[c].notna().sum()
            print(f"{c}: {count}")
    

# Example usage:
count_non_empty_rows()
