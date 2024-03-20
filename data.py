import pickle
import pandas as pd
import numpy as np
file_path = './whole_ball_of_wax.pkl'

df = pd.read_pickle('./whole_ball_of_wax.pkl')
df.to_csv('whole_ball_of_wax.csv', index=True)
#print(df['github_urls'])
print(df['github_urls'].nunique())

n_forks = df.useful_forks.apply(len)
n_pullreq = df.merged_pull_req.apply(len)
frk_95p = np.percentile(n_forks, 95, interpolation='higher')
pr_95p = np.percentile(n_pullreq, 95, interpolation='higher')
sample = df[(n_forks > frk_95p) & (n_pullreq > pr_95p)]
print("Length of sample:", len(sample))

# 445 PR -> 207
n_PR = np.sum(sample.merged_pull_req.apply(len))
# 1648 FORKS -> 312
n_FORKS = np.sum(sample.useful_forks.apply(len))

if n_PR != 445 or n_FORKS != 1648:
    raise Exception("Redo 95-5 calculation!")

n_PR_strat = 207
n_FORKS_strat = 312