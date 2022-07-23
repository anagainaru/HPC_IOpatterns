import argparse
from difflib import SequenceMatcher
from itertools import cycle
from itertools import islice
import json
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import sys

# Parse the JSON log and extract patterns
# Usage: 
#    python extract_patterns_json.py json_file requested_ranks
#                                    requested_execution_time [options]
#    Options: -o output file (default: output.json)
#             -v verbose on (default: False)
#             -i individual patterns on (defaut: False) 
# The individual patterns options allows to repeat patterns that occur only
# once (for which interpolation will fail).

individual_patterns = False
verbose = False

def string_distance(a, b):
    return SequenceMatcher(None, a, b).ratio()

def roundrobin(iterables):
    """Yields an item from each iterable, alternating between them.

        >>> list(roundrobin(['ABC', 'D', 'EF']))
        ['A', 'D', 'E', 'B', 'F', 'C']

    This function produces the same output as :func:`interleave_longest`, but
    may perform better for some inputs (in particular when the number of
    iterables is small).

    """
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = cycle(iter(it).__next__ for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))

# Populate the log with a start and end flag to force a min of two clusters
def add_edges(events_time, events_type):
    min_ts = min([min(events_time[rank]) for rank in events_time])
    max_ts = max([max(events_time[rank]) for rank in events_time])
    for rank in events_time:
        if max_ts - events_time[rank][0] < events_time[rank][0] - min_ts:
            # Populate with a START flag at the beginning of the execution
            events_time[rank].insert(0, min_ts)
            events_type[rank].insert(0, ".DEBUGSTART")
        if max_ts - events_time[rank][-1] > events_time[rank][-1] - min_ts:
            # Populate with an END flag at the end of the execution
            events_time[rank].append(max_ts)
            events_type[rank].append(".DEBUGEND")
    return {rank: [(i - min_ts) / 1000000 for i in events_time[rank]]
            for rank in events_time}, events_type

# Read the json file and keep events timestamp and type
def read_json_data(file_name):
    inf = open(file_name, "r")
    events_time = {}
    events_type = {}
    json_data = json.load(inf)
    for entry in json_data:
        if entry["name"][0] == ".":
            continue
        if (entry["pid"], entry["tid"]) not in events_time:
            events_time[(entry["pid"], entry["tid"])] = []
            events_type[(entry["pid"], entry["tid"])] = []
        events_time[(entry["pid"], entry["tid"])].append(entry["ts"])
        events_type[(entry["pid"], entry["tid"])].append(entry["name"])
    inf.close()
    return add_edges(events_time, events_type)

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
    if len(labels) == max(labels) - 1:
        return False
    if max_delay > 3:
        return False
    return True

# Hierarchical clustering for the events series 
def find_clusters(events_time, end_marker=False):
    events_delay = [(events_time[i] - events_time[i-1])
                    for i in range(1,len(events_time))]
    labels = [0] * len(events_time)
    # if end marker exists
    if end_marker: # the first split is to seprate the end event from the rest
        labels[-1] = 1
    best_clusters = [0, labels]
    if len(labels) == 1:
        return labels
    while len(events_delay) > 0:
        # Split clusters on the largerst delay between events
        max_delay = max([events_delay[i] for i in range(len(events_delay))
                         if labels[i]==labels[i+1]])
        split_index = next(i for i in range(len(events_delay))
                       if events_delay[i]==max_delay)
        if verbose:
            print("[dbg] Split between timestamp", events_time[split_index],
              events_time[split_index+1])
        # if the clusters start computing the silhouette, update the value for
        # the current selection (unless this is the first split)
        if max_delay <= 60 and best_clusters[0] == 0 and max(labels) > 0:
            silhouette_avg = silhouette_score(events_time.reshape(-1, 1), labels)
            best_clusters = [silhouette_avg, labels[:]]
            if verbose:
                print("[dbg] Store current cluster with a score of",
                      silhouette_avg)
        labels = create_labels(labels, split_index)
        if cannot_split_clusters(labels, max_delay):
            break

        # Compute the silhouette score which gives a score for the density and
        # separation of the formed clusters (only if the delay between events
        # is less than a minute, otherwise save the clusters)
        silhouette_avg = 0
        if max_delay <= 60:
            silhouette_avg = silhouette_score(events_time.reshape(-1, 1), labels)
        if verbose:
            print("[dbg] Clustering score", silhouette_avg)
        if max_delay <= 60 and silhouette_avg > best_clusters[0]:
            if verbose:
                print("[dbg] BEST cluster", best_clusters[0], silhouette_avg)
            best_clusters = [silhouette_avg, labels[:]]
    if best_clusters[0] == 0:
            best_clusters = [silhouette_avg, labels[:]]
    if verbose:
        print("[dbg] Total clusters", max(best_clusters[1]) + 1)
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

# Extract all the event patterns describing patterns and their frequency
def find_patterns(labels, events_type, events_time, pattern_list, rank):
    patterns = {}
    cluster_edges = [0] + [i+1 for i in range(len(labels) - 1)
                           if labels[i] != labels[i+1]] + [len(labels) + 1]
    time_clusters = {cluster_edges[i-1] : events_time[cluster_edges[i-1]:cluster_edges[i]]
                     for i in range(1, len(cluster_edges))}
    time_log = [(min(time_clusters[i]), max(time_clusters[i])) for i in time_clusters]
    pattern_list, log = get_count_pattern(cluster_edges, events_type, pattern_list)
    # Add timing information over the log: (pattern_id, time_start, time_end)
    log = [(log[i], time_log[i][0], time_log[i][1], rank) for i in range(len(log))]
    if verbose:
        print("[dbg] Total patterns:", len(pattern_list.keys()), pattern_list)
        print("[dbg] The current TAU log:", [(i[1],i[2]) for i in log])
        print("[dbg] List of patterns:", [i[0] for i in log])
    return pattern_list, log

# Extract the start clusters based on patterns across all the ranks
# The log contains a list of (pattern_id, time_start, time_end)
def extract_start_clusters(log, min_ts, max_ts):
    start_idx = min_ts
    for rank in log:
        log_patterns = [i[0] for i in log[rank]]
        # if there are patterns occuring more than once
        if len(log_patterns) > len(set(log_patterns)):
            # find the first pattern that occurs more than once
            idx = next(i for i in range(1, len(log_patterns))
                       if log_patterns.count(log_patterns[i]) > 1)
            idx -= 1
        else:
            # otherwise take all events that are closer to beginning if any
            idx = [i for i in range(len(log_patterns))
                   if log[rank][i][2] - min_ts < max_ts - log[rank][i][2]]
            if len(idx) > 0:
                idx = idx[0]
            else:
                idx = -1
        if idx >= 0:
            # make sure the begin section does not exceed 1/3 of execution
            limit = min_ts + (max_ts - min_ts) * 0.3
            idx = [i for i in range(0, idx + 1) if log[rank][i][2] < limit]
            if len(idx) > 0:
                idx = max(idx)
                start_idx = max(start_idx, log[rank][idx][2])
    return start_idx

# Extract the end clusters based on patterns across all the ranks
# The log contains a list of (pattern_id, time_start, time_end)
def extract_end_clusters(log, min_ts, max_ts):
    # the end section will always include the "program end" entry
    end_idx = max_ts
    for rank in log:
        log_patterns = [i[0] for i in log[rank]]
        # if not all patterns are occuring only once
        if len(log_patterns) > len(set(log_patterns)):
            # find the last pattern that occurs more than once
            idx = next(i for i in reversed(range(1, len(log_patterns)))
                       if log_patterns.count(log_patterns[i]) > 1)
            idx += 1
        else: # otherwise take all events that are closer to the end if any
            idx = [i for i in range(len(log_patterns))
                   if log[rank][i][0] - min_ts > max_ts - log[rank][i][1]]
            if len(idx) > 0:
                idx = idx[0]
            else:
                idx = -1
        if idx >= 0:
            end_idx = min(end_idx, log[rank][idx][1])
    return end_idx

def interpolate_comp_pattern(log, total_exec, req_exec, rank, degree=1):
    if total_exec > req_exec:
        # cut all the events that exceed the requested execution time
        return [i for i in log if i[2] < req_exec]
    # if the requested time is larger than the existing log, extrapolate
    pattern_ids = set([i[0] for i in log])
    for pattern in pattern_ids:
        ts_series = [i[1] for i in log if i[0]==pattern]
        ts_series_end = [i[2] for i in log if i[0]==pattern]
        if len(ts_series) < 5:
            log += repeat_comp_pattern(pattern, total_exec, req_exec,
                                       ts_series, ts_series_end, rank)
        else:
            try:
                #The use of degree=1 signifies a linear fit.
                fit = np.polyfit(range(len(ts_series)), ts_series, degree)
                if verbose:
                    print("[dbg] Fit for cluster pattern", pattern, fit)
                np.seterr(invalid='ignore')
                line = np.poly1d(fit)
                cnt = len(ts_series)
                while True:
                    ts = line(cnt)
                    if ts > req_exec:
                        break
                    log += [(pattern, ts_series[cnt % len(ts_series)],
                             ts_series_end[cnt % len(ts_series)], rank, ts)]
                    cnt += 1
            except:
                log += repeat_comp_pattern(pattern, total_exec, req_exec,
                                           ts_series, ts_series_end, rank)
    return log

# Decrease or increase the total execution time of the log
def update_exec_pattern(log, start_ts, end_ts, req_exec, degree=1):
    req_log = {rank:[] for rank in log}
    total_exec = int(max([max([i[2] for i in log[rank]]) for rank in log]))
    shift = req_exec - total_exec
    if verbose:
        print("[dbg] Shift by:", shift)
    for rank in log:
        # keep the start pattern
        req_log[rank] += [i for i in log[rank] if i[2] <= start_ts]
        # interpolate the middle pattern
        if verbose:
            print("[dbg] Generate extended log for rank", rank)
        req_log[rank] += interpolate_comp_pattern(
                [i for i in log[rank] if i[2] > start_ts and i[1] < end_ts],
                end_ts - start_ts, req_exec - (total_exec - end_ts), rank, degree=degree)
        # shift the end pattern to the end of the request time
        req_log[rank] += [(i[0], i[1], i[2], rank, i[1]+shift)
                          for i in log[rank] if i[1] >= end_ts]
    return req_log

# extract clusters of ranks that have the exact same behavior
def get_rank_exact_match(log):
    rank_pattern = {}
    for rank in log:
        pattern = "".join([str(i[0]) for i in log[rank]])
        if pattern not in rank_pattern:
            rank_pattern[pattern] = []
        rank_pattern[pattern].append(rank)
    return rank_pattern

# return clusters of ranks with the same behavior
# Example output: [[0], [1, 2, 3, 4], [5, 6, 7, 8, 9]]
def get_rank_pattern(log):
    rank_pattern = get_rank_exact_match(log)
    words = np.array(list(rank_pattern.keys())).reshape(-1, 1)
    best_clusters = (0, list(range(len(words))))
    for true_k in range(2, len(words)):
        model = KMeans(n_clusters=true_k, init='k-means++',
                       max_iter=100, n_init=1)
        cluster = model.fit(words)
        if len(cluster.labels_)==1 or len(cluster.labels_)==len(words):
            silhouette_avg = 0
        else:
            silhouette_avg = silhouette_score(words, cluster.labels_)
        if silhouette_avg > best_clusters[0]:
            best_clusters = (silhouette_avg, cluster.labels_)
    # parse the clusters and create groups of rank ids
    rank_clusters = []
    words = [i[0] for i in words]
    for cluster_id in range(max(best_clusters[1]) + 1):
        temp = [rank_pattern[words[i]] for i in range(len(best_clusters[1]))
                if best_clusters[1][i] == cluster_id]
        rank_clusters.append([])
        for i in temp:
            rank_clusters[-1] += i
    return rank_clusters

# decreate or increase the number of ranks in the log
def update_rank_pattern(log, total_ranks, req_ranks, variability=0):
    total_ranks = len(set(i[0] for i in log))
    if req_ranks < total_ranks:
        # delete the extra ranks from the log
        for rank in range(req_ranks, total_ranks):
            if verbose:
                print("[dbg] Delete", rank)
            # delete all entries (tids) with pid = rank
            del_list = [i for i in log if i[0]==rank]
            for i in del_list:
                del log[rank]
    else:
        # find clusters of ranks with the same bahavior: [[0], [1, 2], [3]]
        rank_cluster = get_rank_pattern(log)
        # repeat the ranks that do not have individual behaviors
        rank_pattern = [i for i in rank_cluster if len(i) > 1]
        rank_pattern = list(roundrobin(rank_pattern))
        if len(rank_pattern) == 0: # if all have individual patterns
            rank_pattern = list(range(total_ranks)) # repeat all ranks
        # add rank behavior in order based on the patterns found
        cnt = 0
        for rank in range(total_ranks, req_ranks):
            if verbose:
                print("[dbg] Rank %d will have the same pattern as rank %d" %(
                    rank[0], rank_pattern[rank % len(rank_pattern)]))
                if variability > 0:
                    print("[dbg]  - added variability between (-%2.1f and %2.1f)" %(
                        variability, variability))
            # the log needs to contain all the threads for the chosen rank
            target_rank = rank_pattern[rank % len(rank_pattern)]
            tid_list = [i[1] for i in log if i[0]==target_rank]
            for tid in tid_list:
                log[(rank, tid)] = log[(target_rank, tid)][:]
                if variability > 0:
                    # add noise to the timestamp of the pattern, either to the original 
                    # timestamp or the interpolated value
                    noise = np.random.uniform(-variability, variability,
                                              len(log[(rank, tid)]))
                    noise = [log[(rank, tid)][i][1]+noise[i]
                             if len(log[(rank, tid)][i])==4
                             else log[(rank, tid)][i][4]+noise[i]
                             for i in range(len(log[(rank, tid)]))]
                    # add the updated value to the new log
                    log[(rank, tid)] = [(log[(rank, tid)][i][0], log[(rank, tid)][i][1],
                                         log[(rank, tid)][i][2], log[(rank, tid)][i][3],
                                         max(0, noise[i]))
                                 for i in range(len(log[(rank, tid)]))]
    return log

# Read the json file and keep a dictionary with strings
# related to each timestamp
def read_time_to_string(file_name):
    inf = open(file_name, "r")
    time_to_string = {}
    json_data = json.load(inf)
    min_ts = min([entry["ts"] for entry in json_data])
    for entry in json_data:
        if (entry["pid"], entry["tid"]) not in time_to_string:
            time_to_string[(entry["pid"], entry["tid"])] = {}
        time_to_string[(entry["pid"], entry["tid"])][(entry["ts"]-min_ts)/1000000] = entry
    inf.close()
    return time_to_string

# Create a JSON file from the log based on the input JSON
# log is a dict {rank: [(pattern_id, initial_ts_start, initial_ts_end, initial_rank)]}
# with the possibility of having another element at the end with the new timestamp
def from_pattern_create_log(log, input_file, output_file):
    max_exec = 0
    time_to_string = read_time_to_string(input_file)
    data = []
    for rank in log:
        if verbose:
            print("[dbg] Writing log for rank %s to the output file" %(rank[0]))
        for pattern in log[rank]:
            # get all the entries occuring between the timestamps
            create_events = [i for i in time_to_string[pattern[3]]
                             if i <= pattern[2] and i >= pattern[1]]
            delay = 0
            if len(pattern)>4:
                max_exec = max(max_exec, pattern[4])
                delay = pattern[4] - pattern[1]
            else:
                max_exec = max(max_exec, pattern[2])
            event_list = [time_to_string[pattern[3]][i] for i in create_events]
            for event in event_list:
                temp_event = {i:event[i] for i in event}
                temp_event["pid"] = rank[0]
                temp_event["tid"] = rank[1]
                temp_event["ts"] = int(temp_event["ts"] + delay * 1000000)
                data.append(temp_event)
    print("Creating a TAU log file with %s ranks and %s execution time" %(
        len(log.keys()), max_exec))
    with open(output_file, 'w') as f:
        f.write(
        '[' +
        ',\n'.join(json.dumps(i) for i in data) +
        ']\n')
    print("DONE. Output json file stored in", output_file)
    return 0

def parse_input_argument():
    global individual_patterns, verbose
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='Input TAU json file')
    parser.add_argument('req_ranks', type=int, help='Number of requested ranks')
    parser.add_argument('req_exec', type=int,
                        help='Requested execution time in seconds')
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="Print debug information")
    parser.add_argument("-i", "--interpolate", action='store_true',
                        help="Repeat only log patterns that can be interpolated")
    parser.add_argument("-o", "--output", default="output.json",
                        help='Output file to store the new JSON log')
    parser.add_argument("-d", "--degree", type=int, default=1,
                        help='Interpolation polynomial degree. Default: linear')
    parser.add_argument("-r", "--rankvar", type=int, default=0,
                        help='Variability among rank duplication. Adds a random noise' \
                              ' with a random distribution with a center of 0 and' \
                              ' length of value (in seconds). Default: 0 (no variability)')
    parser.add_argument("-s", "--stats", action='store_true',
                        help='Only show stats about the TAU log, do not create' \
                             ' a new one. The requested time and ranks will be ignored')
    args = parser.parse_args()
    if args.interpolate:
        individual_patterns = True
    if args.verbose:
        verbose = True
    return args

if __name__ == '__main__':
    args = parse_input_argument()
    req_ranks = args.req_ranks
    req_exec = args.req_exec
    labels = {}
    # read the json TAU file
    events_time, events_type = read_json_data(args.infile)
    min_ts = min([min(events_time[rank]) for rank in events_time])
    max_ts = max([max(events_time[rank]) for rank in events_time])
    print("Number of ranks %d" %(len(set([i[0] for i in events_time.keys()]))))
    print("Execution time %d seconds" %(max_ts - min_ts))
    if args.stats:
        print("The -stats flag was provided, exiting without creating the output log")
        exit()
    pattern_list = {}
    log = {}
    for rank in events_time:
        if verbose:
            print("[dbg] Extract clusters for rank", rank)
        labels[rank] = find_clusters(
                np.array(events_time[rank]),
                end_marker=(events_type[rank][-1]=="program exit"))
        pattern_list, log[rank] = find_patterns(labels[rank], events_type[rank],
                                          events_time[rank], pattern_list, rank)
    start_ts = extract_start_clusters(log, min_ts, max_ts)
    end_ts = extract_end_clusters(log, min_ts, max_ts)
    if verbose:
        print("[dbg] Start position", start_ts)
        print("[dbg] End position", end_ts)
    
    if (max_ts - min_ts) != req_exec:
        log = update_exec_pattern(log, start_ts, end_ts, req_exec,
                                  degree=args.degree)
    if len(events_time.keys()) != req_ranks:
        log = update_rank_pattern(log, len(events_time.keys()), req_ranks,
                                  variability=args.rankvar)

    from_pattern_create_log(log, args.infile, args.output)
