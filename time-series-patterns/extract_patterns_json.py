import json
import numpy as np
from sklearn.metrics import silhouette_score
import sys

# Parse the JSON log and extract patterns
# Usage: 
#    python extract_patterns_json.py json_file

# Read the json file and keep events timestamp and type
def read_json_data(file_name):
    inf = open(file_name, "r")
    events_time = {}
    events_type = {}
    json_data = json.load(inf)
    for entry in json_data:
        if entry["pid"] not in events_time:
            events_time[entry["pid"]] = []
            events_type[entry["pid"]] = []
        events_time[entry["pid"]].append(entry["ts"])
        events_type[entry["pid"]].append(entry["name"])
    inf.close()
    min_ts = min([min(events_time[rank]) for rank in events_time])
    max_ts = max([max(events_time[rank]) for rank in events_time])
    print("Execution time %d seconds" %((max_ts - min_ts) / 1000000))
    return {rank: [(i - min_ts) / 1000000 for i in events_time[rank]]
            for rank in events_time}, events_type

# update labels based on the new cluster split
def create_labels(labels, split_index):
    new_label = max(labels) + 1
    current_label = labels[split_index]
    for i in range(split_index+1, len(labels)):
        if labels[i] != current_label:
            break
        labels[i] = new_label
    return labels

# Criterias to terminate the clustering before reaching individual
# events. Currently, the max delay between events needs to be over 3 seconds
def cannot_split_clusters(labels, max_delay):
    if max_delay > 3:
        return False
    return True

# Hierarchical clustering for the events series 
def find_clusters(events_time):
    events_delay = [(events_time[i] - events_time[i-1])
                    for i in range(1,len(events_time))]
    labels = [0] * len(events_time)
    best_clusters = [0, labels]
    while len(events_delay) > 0:
        # Split clusters on the largerst delay between events
        max_delay = max([events_delay[i] for i in range(len(events_delay))
                         if labels[i]==labels[i+1]])
        split_index = [i for i in range(len(events_delay))
                       if events_delay[i]==max_delay][0]
        print("Split between timestamp", events_time[split_index],
              events_time[split_index+1])
        # if the clusters start computing the silhouette, update the value for
        # the current selection
        if max_delay <= 60 and best_clusters[0]==0:
            silhouette_avg = silhouette_score(events_time.reshape(-1, 1), labels)
            best_clusters = [silhouette_avg, labels[:]]
            print("Store current cluster with a score of", silhouette_avg)
        labels = create_labels(labels, split_index)

        # Compute the silhouette score which gives a score for the density and
        # separation of the formed clusters (only if the delay between events
        # is less than a minute, otherwise save the clusters)
        silhouette_avg = 0
        if max_delay <= 60:
            silhouette_avg = silhouette_score(events_time.reshape(-1, 1), labels)
        print("Clustering score", silhouette_avg)
        if max_delay <= 60 and silhouette_avg > best_clusters[0]:
            print("BEST cluster", best_clusters[0], silhouette_avg)
            best_clusters = [silhouette_avg, labels[:]]
        if cannot_split_clusters(labels, max_delay):
            break
    if best_clusters[0] == 0:
            best_clusters = [silhouette_avg, labels[:]]
    print("Total clusters", max(best_clusters[1]))
    return best_clusters[1]

# unorder and only count (not file information)
def get_count_pattern(cluster_edges, events_type, pattern_list):
    optype_cluster = [events_type[cluster_edges[i-1]:cluster_edges[i]]
                      for i in range(1, len(cluster_edges))]
    count_pattern = [{optype : cluster.count(optype) for optype in set(cluster)} for cluster in optype_cluster]
    # example count pattern [{'fprintf': 7, 'fwrite': 12}, {'fprintf': 10, 'fwrite': 14}]
    log = []
    cnt = len(pattern_list.keys())
    for pattern in count_pattern:
        # patterns have {operation: count}
        pattern_string = [key+":"+str(pattern[key]) for key in pattern]
        pattern_string.sort()
        pattern_string = "-".join(pattern_string)
        # update the list of all existing patterns 
        if pattern_string not in pattern_list:
            pattern_list[pattern_string] = cnt
            cnt += 1
        log.append(pattern_list[pattern_string])
    return pattern_list, log

def add_file_information():
    return 0

# Extract all the event patterns describing patterns and their frequency
def find_patterns(labels, events_type, events_time, pattern_list):
    patterns = {}
    cluster_edges = [0] + [i+1 for i in range(len(labels) - 1)
                           if labels[i] != labels[i+1]] + [len(labels) + 1]
    time_clusters = {cluster_edges[i-1] : events_time[cluster_edges[i-1]:cluster_edges[i]]
                     for i in range(1, len(cluster_edges))}
    print({i: (min(time_clusters[i]), max(time_clusters[i])) for i in time_clusters})
    pattern_list, log = get_count_pattern(cluster_edges, events_type, pattern_list)
    print("Total patterns:", len(pattern_list.keys()), pattern_list.keys())
    print("The current TAU log:",log)

    # add information on what file is being accessed
    add_file_information()
    return pattern_list, log

# Extract the start clusters based on patterns across all the ranks
def extract_start_clusters(labels):
    return 0

# Extract the end clusters based on patterns across all the ranks
def extract_end_clusters(labels):
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python %s log_file" %(sys.argv[0]))
        exit()
    
    labels = {}
    # read the json TAU file
    events_time, events_type = read_json_data(sys.argv[1])
    pattern_list = {}
    log = {}
    for rank in events_time:
        print("Extract clusters for rank", rank)
        labels[rank] = find_clusters(np.array(events_time[rank]))
        pattern_list, log[rank] = find_patterns(labels[rank], events_type[rank],
                                          events_time[rank], pattern_list)
    extract_start_clusters(labels)
    extract_end_clusters(labels)

    rank = 1
    print(set(events_type[rank]))
