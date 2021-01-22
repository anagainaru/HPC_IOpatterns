import sys
import pandas as pd
from collections import Counter
import seaborn as sns
from sklearn.metrics.pairwise import euclidean_distances, manhattan_distances
import matplotlib.pyplot as plt
import hdbscan
import numpy as np
import os

sns.set()

# classification is a dictionary where cl[i] = [list of classes i is part of]
# i is the index in the dataframe
# the classes are hierarchical as the algorithm splits the dataset
classification = {}

# default path to save the cluster information
path = "./test.clusters/"

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

# get the child id and the number of apps in this cluster
# for the child described by the column in the dataframe
def get_child_info(df, distance, column_name):
    child_id = int(df[df.distance == distance][column_name].values[0])
    count = int(df[df.parent == child_id]["size"].values[0])
    return child_id, count

# populate the classification dictionary with the list of
# splits a datapoint goes through in the hierarchy of classes
def classify_dataset(entry, df, class_list, add_entry=True):
    global classification
    # if the entry is an array index
    if len(df[df.parent == entry]) == 0:
        classification[entry] = class_list
        return
    temp_list = class_list[:]
    # if the entry's parent was a split point we add the entry to the list
    if add_entry:
        temp_list.append(entry)
    
    # if the current entry is a parent flag the children
    add_entry = False
    if df[df.parent==entry]["distance"].values[0] > 0:
        add_entry = True
    left_id = int(df[df.parent == entry]["left_child"].values[0])
    right_id = int(df[df.parent == entry]["right_child"].values[0])
    
    classify_dataset(left_id, df, temp_list, add_entry)
    classify_dataset(right_id, df, temp_list, add_entry)

# keep only the entries in the dataframe corresponding to the 
# chosen indexes and create cluster labels for the two children
def filter_dataset(df, left_cl_idx, right_cl_idx, left_count, right_count):
    df_temp = df.iloc[left_cl_idx, :].reset_index(drop=True)
    result = pd.concat(
            [df_temp, df.iloc[right_cl_idx, :].set_index(pd.Index(
                [i for i in range(len(df_temp),
                                  len(df_temp) + right_count)]))])
    cluster_labels = [0] * left_count + [1] * right_count
    assert(len(result) == len(cluster_labels)), \
            "ERR! Cluster size and labels mismatch" \
            "at distance %f" %(distance)
    result["Cluster"] = cluster_labels
    return result

# check if the right and left clusters detected at this level
# are consistent with the ones returned by the single_linkage_tree function
def check_cluster_goodness(cluster, distance, left_cl_idx, right_cl_idx):
    # Function that returns all the clusters at this level 
    cl = cluster.single_linkage_tree_.get_clusters(
            distance, min_cluster_size=1)
    
    # The two clusters detected should have the same id
    # in the list of all clusters
    assert (len(set([cl[i] for i in left_cl_idx])) == 1), \
            "Error at the left cluster for distance %f" %(distance)
    assert (len(set([cl[i] for i in right_cl_idx])) == 1), \
            "Error at the right cluster for distance %f" %(distance)

def save_clusters(distance, df, cluster_labels=[]):
    global path
    if len(df) == len(cluster_labels):
        df["Cluster"] = cluster_labels
    df.to_csv(path + "cluster.%.3f" %(distance) + ".csv", index=False)

def analyze_cluster_formation(dataset, df, cluster, split_distances):
    global classification
    for distance in split_distances:
        # for every split in the clustering process
        left_id, left_count = get_child_info(df, distance,
                                             "left_child")
        right_id, right_count = get_child_info(df, distance,
                                               "right_child")
        # identify the left and right cluster ids
        print("Split at distance %f" %(distance))

        # get the index of the entries from the dataframe that have been split
        # at this level and dump the rest of the entries
        left_cl_idx = [i for i in range(len(dataset))
                       if left_id in classification[i]]
        assert(len(left_cl_idx) == left_count), \
                "Error identifying the clusters at distance %f" %(distance)
        right_cl_idx = [i for i in range(len(dataset))
                        if right_id in classification[i]]
        assert(len(right_cl_idx) == right_count), \
                "Error identifying the clusters at distance %f" %(distance)

        # only keep the entries of the entries that were split
        # in two clusters at this level
        filtered_df = filter_dataset(
                dataset, left_cl_idx, right_cl_idx, left_count, right_count)
        print("Left cluster (%d): %d runs %s" %(
            left_id, left_count,
            filtered_df[filtered_df.Cluster==0]["apps"].unique()))
        print("Right cluster (%d): %d runs %s" %(
            right_id, right_count,
            filtered_df[filtered_df.Cluster==1]["apps"].unique()))

        # make sure the clusters are correct
        check_cluster_goodness(cluster, distance, left_cl_idx, right_cl_idx)
        save_clusters(distance, filtered_df)

def main(top_apps=6, jobs_per_app=16):
    global classification, path
    if len(sys.argv) < 2:
        print("Usage: %s fetures_file" %(sys.argv[0]))
        return

    index = sys.argv[1].rfind(".")
    path = sys.argv[1][:index]+".clusters/"
    if not os.path.exists(path):
        os.mkdir(path)

    # read the data and extract the clusters
    df, cluster = default_dataset(paths=[sys.argv[1]])
    # save the cluster with all the labes
    save_clusters(0, df, cluster.labels_)

    # extract the hierarchy of binary splits
    tree = cluster.single_linkage_tree_.to_pandas()
    # extract the distances at which the cluster is split in two
    split_distances = tree[tree.distance > 0]["distance"].values
    # get the root node in the tree (containing all the datapoints)
    root = tree.iloc[tree['distance'].argmax()]["parent"]
    # for each datapoint get the list of classes it goes through
    # from the root to the least general class
    print("Start classification from", root)
    classify_dataset(root, tree, [])
    analyze_cluster_formation(df, tree, cluster, split_distances)

    # plot the tree associated with the clusters
    cluster.single_linkage_tree_.plot(cmap='viridis', colorbar=True)
    #plt.show()
    plt.savefig(path + 'cluster_tree.png')
    print("Clusters successfully saved in folder", path)

if __name__ == "__main__":
    main()
