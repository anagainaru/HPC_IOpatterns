#  Created on: Feb 9, 2021
#      Author: Ana Gainaru gainarua@ornl.gov
# Script to extract and gather features from darshan logs into a data frame

import numpy as np
import csv
import os.path
import sys

from extract_metadata_features import metadata_features
from extract_aggregated_features import aggregated_features
from extract_dxt_features import dxt_features

def log_scale_metrics(feature_list, small_value=10 ** -5):
    number_columns = list(feature_list.keys())
    columns = [x for x in number_columns if "perc" not in x.lower()]
    print("Applying log10() to the columns {}".format(columns))
    for c in columns:
        # skip entries that are not float
        try:
            float(feature_list[c])
        except:
            continue
        if c == 'IO_runtime' or c == 'RAW_nprocs':
            feature_list[c.replace("RAW", "LOG10")] = np.log10(
                    feature_list[c] + small_value)
        else:
            feature_list[c.replace("POSIX", "POSIX_LOG10")] = np.log10(
                    feature_list[c] + small_value)
    return feature_list

def write_features_to_file(feature_list, filename):
    # write the feature list in a csv file
    write_header = True
    if os.path.isfile(filename):
        write_header = False
    with open(filename, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(feature_list.keys()))
        if write_header:
            writer.writeheader()
        writer.writerows([feature_list])

def create_empty_dict():
    feature_list = {}
    with open("./features.header") as f:
        for line in f:
            feature_list[line[:-1]] = 0
    print(len(feature_list))
    return feature_list

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python %s darshan_file system_procs [save_name]" %(
            sys.argv[0]))
        exit()
    
    save_name = 'features.csv'
    if len(sys.argv) > 3:
        save_name = sys.argv[3]

    darshan_file = "%s" %(sys.argv[1])
    system_procs = int(sys.argv[2])

    # extract the features from the metadata information
    feature_list = create_empty_dict()
    metadata_features, IOtype_list = metadata_features(
            darshan_file, system_procs)
    #print(metadata_features)
    print(len(feature_list))

    feature_list.update(metadata_features)
    # extract features from the  aggregated logs
    features, IOtype_used= aggregated_features(
            darshan_file, IOtype_list, metadata_features["Total_runtime"])
    for IOtype in IOtype_used:
        feature_list["is_" + IOtype] = 1
    #print(set(features) - set(feature_list.keys()))
    feature_list.update(features)
    print(len(feature_list))

    feature_list["IO_runtime"] = 0
    feature_list["Read_runtime"] = 0
    feature_list["Write_runtime"] = 0
    feature_list["Metadata_runtime"] = 0
    for IOtype in IOtype_list:
        feature_list["IO_runtime"] += feature_list["%s_IO_runtime" %(IOtype)]
        feature_list["Read_runtime"] += \
                feature_list["%s_read_runtime" %(IOtype)]
        feature_list["Write_runtime"] += \
                feature_list["%s_write_runtime" %(IOtype)]
        feature_list["Metadata_runtime"] += \
                feature_list["%s_metadata_runtime" %(IOtype)]
    feature_list["IO_ranks_perc"] = feature_list["IO_ranks"] /\
            feature_list["Total_procs"]
    # add LOG10 metrics to be consistent with Mihailo Isakov's study
    #feature_list = log_scale_metrics(feature_list)

    # if DXT logs are available add dxt_features(df)
    #if os.path.isfile(darshan_file + ".dxt"):
    #    features = dxt_features(darshan_file + ".dxt")
    #    feature_list.update(features)

    write_features_to_file(feature_list, save_name)
    print("Features saved in file %s" %(save_name))
