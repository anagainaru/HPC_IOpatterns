import sys
import pandas as pd
from collections import Counter
import seaborn as sns
from sklearn.metrics.pairwise import euclidean_distances, manhattan_distances
import matplotlib.pyplot as plt
import hdbscan
import numpy as np

from feature_selector import FeatureSelector

sns.set()

def default_dataset(paths):
    df = pd.read_csv(paths[0])
    # Use HDBSCAN
    log_columns = set([c for c in df.columns if 'perc' in c.lower()
                       or 'log10' in c.lower()])
    log_columns -= set(['Total_procs', 'RAW_runtime', 'users',
                        'apps', 'apps_short'])
    clusterer = hdbscan.HDBSCAN(min_samples=10, cluster_selection_epsilon=5,
                                metric='manhattan', gen_min_span_tree=True,
                                core_dist_n_jobs=8)
    clusterer.fit(df[log_columns])
    return df, clusterer

def cluster_properties(df, cluster):
    print("Number of clusters", max(cluster))
    print("Properties of cluster 0 compared to the rest")

    # binary labels to show the difference between cluster 0 and the rest
    labels_cluster = [1 if cluster[i] > 0 else 0 for i in range(len(cluster))]
    fs = FeatureSelector(data = df, labels = labels_cluster)
    fs.identify_collinear(correlation_threshold=0.975)
    correlated_features = fs.ops['collinear']
    #print(len(correlated_features), correlated_features[:5])
    #fs.plot_collinear(plot_all=True)
    fs.identify_zero_importance(task = 'classification', eval_metric = 'auc', 
                                n_iterations = 10, early_stopping = True) 
    #zero_importance_features = fs.ops['zero_importance']
    #print(zero_importance_features[:5])
    fs.identify_low_importance(cumulative_importance = 0.99)
    low_importance_features = fs.ops['low_importance']
    #print(len(low_importance_features), low_importance_features[:5])

    df_removed_all = fs.remove(methods = 'all', keep_one_hot=False)
    print('Original Number of Features', df.shape[1])
    print('Final Number of Features: ', df_removed_all.shape[1],
          df_removed_all.columns)

    # print all the apps in each cluster
    df["Cluster_ID"] = cluster
    apps_list = df.groupby("Cluster_ID")["apps"].unique()
    print(apps_list)
    #print(df.groupby(['Cluster_ID']).var().to_dict())
    #print(df.groupby(['Cluster_ID']).var())
    #print(cluster)#, clusterer.probabilities_)

def main(top_apps=6, jobs_per_app=16):
    if len(sys.argv) < 2:
        print("Usage: %s fetures_file" %(sys.argv[0]))
        return

    df, cluster = default_dataset(paths=[sys.argv[1]])
    # print the properties for the final chosen cluster
    cluster_properties(df, cluster.labels_)

    tree = cluster.single_linkage_tree_.to_pandas()
    split_points = tree[tree.distance > 0]["distance"].values

    # Inspect each step when clusters are split into multiple sub-clusters
    for distance in split_points:
        # Skip this step for now
        break
        # get the clusters for this level
        cl = cluster.single_linkage_tree_.get_clusters(
                distance, min_cluster_size=1)
        # print the properties of the cluster at this level
        cluster_properties(df, cl)

    # plot the steps in splitting the data into clusters
    cluster.single_linkage_tree_.plot(cmap='viridis', colorbar=True)
    plt.show()

if __name__ == "__main__":
    main()
