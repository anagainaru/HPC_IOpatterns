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
    #events_delay = {rank: [(events_time[rank][i] - events_time[rank][i-1])/1000000
    #                       for i in range(1,len(events_time[rank]))]
    #                for rank in events_time}
    return [(i - min_ts) / 1000000 for i in events_time], events_type

# Hierarchical clustering for the events series 
def find_clusters():
    # The silhouette_score gives the average value for all the samples.
    # This gives a perspective into the density and separation of the formed
    # clusters
    silhouette_avg = silhouette_score(events_time, cluster_labels)
    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python %s log_file" %(sys.argv[0]))
        exit()
    
    # read the json TAU file
    events_time, events_type = read_json_data(sys.argv[1])
    for rank in events_time:
        find_clusters(events_time[rank])
    rank = 1
    print([i for i in events_delay[rank] if i>10])
    print(set(events_type[rank]))
