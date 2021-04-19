#  Created on: Feb 9, 2021
#      Author: Ana Gainaru gainarua@ornl.gov
# Script to extract and gather features from the darshan metadata section

import re
import os

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
        # keep the order of the IO types: POSIX, HDF5, MPIIO etc
        if "module data" in line:
            IOtype = line[2:line.find(" ",2)]
            if IOtype not in IOindex:
                IOindex[IOtype.replace('-', '')] = len(IOindex)
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

    # the study is not interested in STDIO, we remove it from the list
    if "STDIO" in IOindex:
        del IOindex["STDIO"]
    return metadata, IOindex

def metadata_rw_bytes(metadata, ioIndex):
    feature_list = {}
    if "read_only" not in metadata:
        print("WARNING! Darshan file was not ran with the --file flag")
        for IOtype in ioIndex:
            feature_list["%s_read_write_bytes_perc" %(IOtype)] = -1
            feature_list["%s_read_only_bytes_perc" %(IOtype)] = -1
            feature_list["%s_write_only_bytes_perc" %(IOtype)] = -1
        return feature_list

    # <file_count> <total_bytes> <max_byte_offset>
    for IOtype in ioIndex:
        ro_bytes = [int(i) for i in
                    metadata["read_only"][ioIndex[IOtype]].split(" ")]
        wo_bytes = [int(i) for i in
                    metadata["write_only"][ioIndex[IOtype]].split(" ")]
        rw_bytes = [int(i) for i in
                    metadata["read_write"][ioIndex[IOtype]].split(" ")]
        total_bytes = ro_bytes[1] + wo_bytes[1] + rw_bytes[1]
        if total_bytes == 0:
            continue
        feature_list["%s_read_write_bytes_perc" %(IOtype)] = rw_bytes[1] / total_bytes
        feature_list["%s_read_only_bytes_perc" %(IOtype)] = ro_bytes[1] / total_bytes
        feature_list["%s_write_only_bytes_perc" %(IOtype)] = wo_bytes[1] / total_bytes
    return feature_list

def metadata_unique_bytes(metadata, ioIndex):
    feature_list = {}
    if "unique" not in metadata:
        print("WARNING! Darshan file was not ran with the --file flag")
        for IOtype in ioIndex:
            feature_list["%s_unique_bytes_perc" %(IOtype)] = -1
            feature_list["%s_shared_bytes_perc" %(IOtype)] = -1
        return feature_list
    # <file_count> <total_bytes> <max_byte_offset>
    for IOtype in ioIndex:
        unique_bytes = [int(i) for i in
                        metadata["unique"][ioIndex[IOtype]].split(" ")]
        shared_bytes = [int(i) for i in
                        metadata["shared"][ioIndex[IOtype]].split(" ")]
        total_bytes = unique_bytes[1] + shared_bytes[1]
        if total_bytes == 0:
            continue
        feature_list["%s_unique_bytes_perc" %(IOtype)] = unique_bytes[1] / total_bytes
        feature_list["%s_shared_bytes_perc" %(IOtype)] = shared_bytes[1] / total_bytes
    return feature_list

def metadata_rw_files(metadata, ioIndex):
    if "read_only" not in metadata:
        print("WARNING! Darshan file was not ran with the --file flag")
        return {}
    feature_list = {}
    # <file_count> <total_bytes> <max_byte_offset>
    for IOtype in ioIndex:
        ro_bytes = [int(i) for i in
                    metadata["read_only"][ioIndex[IOtype]].split(" ")]
        wo_bytes = [int(i) for i in
                    metadata["write_only"][ioIndex[IOtype]].split(" ")]
        rw_bytes = [int(i) for i in
                    metadata["read_write"][ioIndex[IOtype]].split(" ")]
        total_bytes = [int(i) for i in
                       metadata["total"][ioIndex[IOtype]].split(" ")][0]
        if total_bytes != ro_bytes[0] + wo_bytes[0] + rw_bytes[0]:
            continue
        if total_bytes == 0:
            continue
        feature_list["%s_read_write_files_perc" %(IOtype)] = rw_bytes[0] / total_bytes
        feature_list["%s_read_only_files_perc" %(IOtype)] = ro_bytes[0] / total_bytes
        feature_list["%s_write_only_files_perc" %(IOtype)] = wo_bytes[0] / total_bytes
    return feature_list

def metadata_unique_files(metadata, ioIndex):
    if "unique" not in metadata:
        print("WARNING! Darshan file was not ran with the --file flag")
        return {}
    feature_list = {}
    # <file_count> <total_bytes> <max_byte_offset>
    for IOtype in ioIndex:
        unique_bytes = [int(i) for i in
                        metadata["unique"][ioIndex[IOtype]].split(" ")]
        shared_bytes = [int(i) for i in
                        metadata["shared"][ioIndex[IOtype]].split(" ")]
        total_bytes = [int(i) for i in
                       metadata["total"][ioIndex[IOtype]].split(" ")][0]
        if total_bytes != unique_bytes[0] + shared_bytes[0]:
            continue
        if total_bytes == 0:
            continue
        feature_list["%s_unique_files_perc" %(IOtype)] = unique_bytes[0] / total_bytes
        feature_list["%s_shared_files_perc" %(IOtype)] = shared_bytes[0] / total_bytes
    return feature_list

def metadata_filename(darshan_file):
    feature_list = {}
    # remove the path to the file and only keep the filename
    filename = os.path.split(darshan_file)[1]
    try:
        feature_list['user'] = re.match(
            r"([a-zA-Z0-9\+]*)_([a-zA-Z0-9_\-.\+]+)_id.*",
            re.findall(r"[a-zA-Z0-9_.\+-]+.log", filename)[0],
            re.MULTILINE).groups()[0]
        feature_list['exec_name'] = re.match(
            r"([a-zA-Z0-9\+]*)_([a-zA-Z0-9_\-.\+]+)_id.*",
            re.findall(r"[a-zA-Z0-9_.\+-]+.log", filename)[0],
            re.MULTILINE).groups()[1]
    except:
        feature_list['user'] = "unknown"
        feature_list['exec_name'] = re.match(
            r"([a-zA-Z0-9\+]*).*",
            re.findall(r"[a-zA-Z0-9_.\+-]+.log", filename)[0],
            re.MULTILINE).groups()[0]

    feature_list['app_name'] = re.match(
            r"([a-zA-Z0-9]+).*", feature_list['exec_name'])
    if feature_list['app_name'] is not None:
        feature_list['app_name'] = feature_list['app_name'].groups(1)[0]
    else:
        feature_list['app_name'] = ""
    return feature_list

def types_IO_used(metadata, IO_used):
    feature_list = {}
    # initialize the IOtypes as false
    interest_IOtypes = ["HDF5", "MPIIO", "ADIOS", "ALPINE", "BB"]
    for IOtype in interest_IOtypes:
        feature_list["is_" + IOtype] = 0
        if IOtype in IO_used:
            feature_list["is_" + IOtype] = 1
    return feature_list

def metadata_features(darshan_file, system_procs, log_count=1):
    metadata, ioIndex = read_metadata(darshan_file)
    feature_list = types_IO_used(metadata, ioIndex.keys())
    # Extract basic information
    feature_list["Total_procs"] = int(metadata["nprocs"][0])
    feature_list["Total_procs_perc"] = float(metadata["nprocs"][0]) \
            / system_procs
    feature_list["Total_runtime"] = int(metadata["run time"][0])
    feature_list["input_param"] = metadata["exe"][0].split(' ', 1)[1]
    feature_list["job_id"] = int(metadata["jobid"][0])
    feature_list["log_count"] = log_count

    # Extract application name and user from the filename
    feature_list.update(metadata_filename(darshan_file))

    # Extract information provided by the --file flag
    feature_list.update(metadata_rw_bytes(metadata, ioIndex))
    feature_list.update(metadata_unique_bytes(metadata, ioIndex))

    # Extract information provided by the --file flag
    feature_list.update(metadata_rw_files(metadata, ioIndex))
    feature_list.update(metadata_unique_files(metadata, ioIndex))
    return feature_list, [s.replace('-', '') for s in ioIndex]
