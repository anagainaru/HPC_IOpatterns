# Script to extract and gather features from darshan logs into a data frame
# -- only for POSIX and MPI-IO calls --
# The format of the output data frame is: Rank File Metric Value

import numpy as np
import pandas as pd
import matplotlib.patches as mpatches
import re
import csv
import os.path
import sys

# Read metadata in the comments of the darshan aggregated log
# obtained with --file appended with the --base options of the parser
def read_metadata(filename):
    metadata = {}
    IOindex = {}
    inf = open(filename)
    for line in inf:
        # ignore blank lines
        if len(line) < 2:
            continue
        # stop when the header section is finished
        if line[0] != "#":
            break
        # keep the order of the IO types: POSIX, STDIO. MPIIO etc
        if "module data" in line:
            IOtype = line[2:line.find(" ",2)]
            if IOtype not in IOindex:
                IOindex[IOtype] = len(IOindex)
        # create key value entries for all the lines
        delimiter = line.find(":")
        if delimiter == -1:
            continue
        key = line[2 : delimiter].lstrip().rstrip()
        value = line[delimiter + 1 : -1].lstrip().rstrip()
        if key not in metadata:
            metadata[key] = []
        metadata[key].append(value)
    inf.close()
    return metadata, IOindex

def metadata_rw_bytes(metadata, ioIndex):
    if "read_only" not in metadata:
        print("WARNING! Darshan file was not ran with the --file flag")
        return {}
    feature_list = {}
    # <file_count> <total_bytes> <max_byte_offset>
    ro_bytes = [int(i) for i in
                metadata["read_only"][ioIndex["POSIX"]].split(" ")]
    wo_bytes = [int(i) for i in
                metadata["write_only"][ioIndex["POSIX"]].split(" ")]
    rw_bytes = [int(i) for i in
                metadata["read_write"][ioIndex["POSIX"]].split(" ")]
    total_bytes = ro_bytes[1] + wo_bytes[1] + rw_bytes[1]
    feature_list["POSIX_read_write_bytes_perc"] = ro_bytes[1] / total_bytes
    feature_list["POSIX_read_only_bytes_perc"] = wo_bytes[1] / total_bytes
    feature_list["POSIX_write_only_bytes_perc"] = rw_bytes[1] / total_bytes
    return feature_list

def metadata_unique_bytes(metadata, ioIndex):
    if "unique" not in metadata:
        print("WARNING! Darshan file was not ran with the --file flag")
        return {}
    feature_list = {}
    # <file_count> <total_bytes> <max_byte_offset>
    unique_bytes = [int(i) for i in
                    metadata["unique"][ioIndex["POSIX"]].split(" ")]
    shared_bytes = [int(i) for i in
                    metadata["shared"][ioIndex["POSIX"]].split(" ")]
    total_bytes = unique_bytes[1] + shared_bytes[1]
    feature_list["POSIX_unique_bytes_perc"] = unique_bytes[1] / total_bytes
    feature_list["POSIX_shared_bytes_perc"] = shared_bytes[1] / total_bytes
    return feature_list

def metadata_features(darshan_file):
    metadata, ioIndex = read_metadata(darshan_file)
    feature_list = {}
    # Extract basic information
    feature_list["Total_procs"] = int(metadata["nprocs"][0])
    feature_list["RAW_runtime"] = int(metadata["run time"][0])

    # Extract information provided by the --file flag
    feature_list.update(metadata_rw_bytes(metadata, ioIndex))
    feature_list.update(metadata_unique_bytes(metadata, ioIndex))
    return feature_list


def read_aggregated_log(darshan_file):
    # Darshan files have the following format:
    # <module> <rank> <record id> <counter> <value> <file name> <mount pt> <fs type>
    df = pd.read_csv(darshan_file, delimiter='\t', comment='#',
                     names=['IOType', 'Rank', 'RecordID', 'Counter', 'Value',
                            'File', 'MountPt', 'FSType'])
    return df

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python %s darshan_file [save_name]" %(sys.argv[0]))
        exit()
    
    save_name = 'features.out'
    if len(sys.argv) > 2:
        save_name = sys.argv[2]

    darshan_file = "%s" %(sys.argv[1])
    # extract the features from the metadata information
    features_list = metadata_features(darshan_file)

    # extract features from the  aggregated logs
    features = aggregated_features(darshan_file)
    features_list.update(features)

    # if DXT logs are available add dxt_features(df)

