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
    return feature_list

def update_allRank_metrics(feature_list, IOtype_list, total_IO_ranks):
    feature_list["IO_ranks_perc"] = feature_list["IO_ranks"] /\
            feature_list["Total_procs"]
    feature_list["Total_read_ranks_perc"] = 0
    feature_list["Total_write_ranks_perc"] = 0
    for IOtype in IOtype_list:
        feature_list["Total_read_ranks_perc"] += \
                feature_list[IOtype + "_read_ranks_perc"]
        feature_list["Total_write_ranks_perc"] += \
                feature_list[IOtype + "_write_ranks_perc"]
        print(IOtype, feature_list[IOtype + "_read_ranks_perc"], feature_list[IOtype + "_write_ranks_perc"], total_IO_ranks)
        # normalize the features for each IOtype
        feature_list[IOtype + "_read_ranks_perc"] /= total_IO_ranks
        feature_list[IOtype + "_write_ranks_perc"] /= total_IO_ranks
    # normalize the overall metrics
    feature_list["Total_read_ranks_perc"] /= total_IO_ranks
    feature_list["Total_write_ranks_perc"] /= total_IO_ranks
    return feature_list

def update_allIO_metrics(feature_list, IOtype_list, IOtype_used):
    # flags for using burst buffers, alpine or adios
    for IOtype in IOtype_used:
        feature_list["is_" + IOtype] = 1
    
    feature_list["IO_runtime_perc"] = 0
    feature_list["Read_runtime_perc"] = 0
    feature_list["Write_runtime_perc"] = 0
    feature_list["Metadata_runtime_perc"] = 0
    # the list of IOtypes captured by darshan: POSIX, MPIIO, HDF5
    for IOtype in IOtype_list:
        # sum the runtime_perc for each type of IO
        feature_list["IO_runtime_perc"] += \
                feature_list["%s_IO_runtime_perc" %(IOtype)]
        feature_list["Read_runtime_perc"] += \
                feature_list["%s_read_runtime_perc" %(IOtype)]
        feature_list["Write_runtime_perc"] += \
                feature_list["%s_write_runtime_perc" %(IOtype)]
        feature_list["Metadata_runtime_perc"] += \
                feature_list["%s_metadata_runtime_perc" %(IOtype)]
        # once the information is no longer needed, normalize it
        feature_list["%s_read_runtime_perc" %(IOtype)] /= \
                feature_list["%s_IO_runtime_perc" %(IOtype)]
        feature_list["%s_write_runtime_perc" %(IOtype)] /= \
                feature_list["%s_IO_runtime_perc" %(IOtype)]
        feature_list["%s_metadata_runtime_perc" %(IOtype)] /= \
                feature_list["%s_IO_runtime_perc" %(IOtype)]
        feature_list["%s_IO_runtime_perc" %(IOtype)] /= \
                feature_list["Total_runtime"]

    # normalize the overall metrics
    feature_list["Read_runtime_perc"] /= feature_list["IO_runtime_perc"]
    feature_list["Write_runtime_perc"] /= feature_list["IO_runtime_perc"]
    feature_list["Metadata_runtime_perc"] /= feature_list["IO_runtime_perc"]
    feature_list["IO_runtime_perc"] /= feature_list["Total_runtime"]

    return update_allRank_metrics(
            feature_list, IOtype_list, feature_list["IO_ranks"])

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python %s darshan_file system_procs [save_name]" %(
            sys.argv[0]))
        exit()
    
    save_name = 'list_of_features.csv'
    if len(sys.argv) > 3:
        save_name = sys.argv[3]

    darshan_file = "%s" %(sys.argv[1])
    system_procs = int(sys.argv[2])

    # extract the features from the metadata information
    feature_list = create_empty_dict()
    print("Default features:", len(feature_list))

    features, IOtype_list = metadata_features(
            darshan_file, system_procs)
    feature_list.update(features)
    print("Metadata features:", len(feature_list))

    # extract features from the  aggregated logs
    features, IOtype_used= aggregated_features(
            darshan_file, IOtype_list, feature_list["Total_runtime"])
    #print(set(features) - set(feature_list.keys()))
    feature_list.update(features)
    print("Aggregated features:", len(feature_list))

    if feature_list["IO_ranks"] == 0:
        print("The application does no IO, no output generated")
        exit()
    # fill in overall information and normalize the remaining data
    feature_list = update_allIO_metrics(feature_list, IOtype_list, IOtype_used)
    print("Overall features:", len(feature_list))

    # if DXT logs are available add dxt_features(df)
    #if os.path.isfile(darshan_file + ".dxt"):
    #    features = dxt_features(darshan_file + ".dxt")
    #    feature_list.update(features)

    write_features_to_file(feature_list, save_name)
    print("Features saved in file %s" %(save_name))
