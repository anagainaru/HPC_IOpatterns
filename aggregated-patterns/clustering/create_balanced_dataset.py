import sys
import numpy as np
import pandas as pd
import seaborn as sns; sns.set()
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from sklearn.decomposition import IncrementalPCA
from scipy import stats
from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import dendrogram
from scipy.cluster.hierarchy import cut_tree

def get_filtered_columns(df):
    filter_columns = list(["user", "exec_name", "app_name"])
    log_columns = set(df.columns) - set(filter_columns)

    filter_columns += list(df[log_columns].std()[df[log_columns].std() < 0.05].index.values)
    filter_columns += list([c for c in df.columns if c not in filter_columns and (max(df[c]) > 1 or min(df[c]) < -1)])

    print("Columns that have low variation", df[log_columns].std()[df[log_columns].std() < 0.05].index.values)
    #df.columns[df.nunique() <= 1])
    # columns that have values over 1 or below -1
    print("Out of bound columns", [c for c in df.columns if c not in filter_columns and (max(df[c]) > 1 or min(df[c]) < -1)])
    print("Filtered fields:", filter_columns)
    return filter_columns

def read_dataset(filename, app_name):
    pd.read_csv(filename, delimiter=',')
    # normalize storage and IO_library
    max_storage = df["storage"].max()
    df["storage"] = df["storage"] / max_storage
    max_io = df["IO_library"].max()
    df["IO_library"] = df["IO_library"] / max_io
    # only keep entries for the given application
    if app_name != "":
        df = df[df.app_name==app_name]
    # drop the duplicates
    df = df.drop_duplicates(keep='last')
    return df

def get_pca_df(df, log_columns):
    pca = PCA(random_state=42)
    pca.fit(df[log_columns])
    var_cumu = np.cumsum(pca.explained_variance_ratio_)
    # find the lowest value for which the var_cumu is above 0.9
    num_pc = min([i for i in range(len(var_cumu)) if var_cumu[i]>0.9])
    pca_components = num_pc
    pca_final = IncrementalPCA(n_components=pca_components)
    df_pca = pca_final.fit_transform(df[log_columns])
    return df_pca

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python %s input_csv application_name [number_saved_entries]" %(
            sys.argv[0]))
        exit()

    app_name = sys.argv[2]

    df = read_dataset(sys.argv[1], app_name) 

    # find the fields that do not give any variation
    filter_columns = get_filtered_columns(df)
    log_columns = set(df.columns) - set(filter_columns)
    print("Clustering based on",len(log_columns), "columns and",len(df),"entries")


    
