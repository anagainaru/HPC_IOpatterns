# Script to extract and gather features from the darshan metadata section
# -- only for POSIX --

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
    feature_list = {}
    if "read_only" not in metadata:
        print("WARNING! Darshan file was not ran with the --file flag")
        feature_list["POSIX_read_write_bytes_perc"] = -1
        feature_list["POSIX_read_only_bytes_perc"] = -1
        feature_list["POSIX_write_only_bytes_perc"] = -1
        return feature_list

    # <file_count> <total_bytes> <max_byte_offset>
    ro_bytes = [int(i) for i in
                metadata["read_only"][ioIndex["POSIX"]].split(" ")]
    wo_bytes = [int(i) for i in
                metadata["write_only"][ioIndex["POSIX"]].split(" ")]
    rw_bytes = [int(i) for i in
                metadata["read_write"][ioIndex["POSIX"]].split(" ")]
    total_bytes = ro_bytes[1] + wo_bytes[1] + rw_bytes[1]
    feature_list["POSIX_read_write_bytes_perc"] = rw_bytes[1] / total_bytes
    feature_list["POSIX_read_only_bytes_perc"] = ro_bytes[1] / total_bytes
    feature_list["POSIX_write_only_bytes_perc"] = wo_bytes[1] / total_bytes
    return feature_list

def metadata_unique_bytes(metadata, ioIndex):
    feature_list = {}
    if "unique" not in metadata:
        print("WARNING! Darshan file was not ran with the --file flag")
        feature_list["POSIX_unique_bytes_perc"] = -1
        feature_list["POSIX_shared_bytes_perc"] = -1
        return feature_list
    # <file_count> <total_bytes> <max_byte_offset>
    unique_bytes = [int(i) for i in
                    metadata["unique"][ioIndex["POSIX"]].split(" ")]
    shared_bytes = [int(i) for i in
                    metadata["shared"][ioIndex["POSIX"]].split(" ")]
    total_bytes = unique_bytes[1] + shared_bytes[1]
    feature_list["POSIX_unique_bytes_perc"] = unique_bytes[1] / total_bytes
    feature_list["POSIX_shared_bytes_perc"] = shared_bytes[1] / total_bytes
    return feature_list

def metadata_rw_files(metadata, ioIndex):
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
    total_bytes = [int(i) for i in
                   metadata["total"][ioIndex["POSIX"]].split(" ")][0]
    if total_bytes != ro_bytes[0] + wo_bytes[0] + rw_bytes[0]:
        return {}
    feature_list["POSIX_read_write_files_perc"] = rw_bytes[0] / total_bytes
    feature_list["POSIX_read_only_files_perc"] = ro_bytes[0] / total_bytes
    feature_list["POSIX_write_only_files_perc"] = wo_bytes[0] / total_bytes
    return feature_list

def metadata_unique_files(metadata, ioIndex):
    if "unique" not in metadata:
        print("WARNING! Darshan file was not ran with the --file flag")
        return {}
    feature_list = {}
    # <file_count> <total_bytes> <max_byte_offset>
    unique_bytes = [int(i) for i in
                    metadata["unique"][ioIndex["POSIX"]].split(" ")]
    shared_bytes = [int(i) for i in
                    metadata["shared"][ioIndex["POSIX"]].split(" ")]
    total_bytes = [int(i) for i in
                   metadata["total"][ioIndex["POSIX"]].split(" ")][0]
    if total_bytes != unique_bytes[0] + shared_bytes[0]:
        return {}
    feature_list["POSIX_unique_files_perc"] = unique_bytes[0] / total_bytes
    feature_list["POSIX_shared_files_perc"] = shared_bytes[0] / total_bytes
    return feature_list

def metadata_filename(darshan_file):
    feature_list = {}
    # remove the path to the file and only keep the filename
    filename = os.path.split(darshan_file)[1]
    try:
        feature_list['users'] = re.match(
            r"([a-zA-Z0-9\+]*)_([a-zA-Z0-9_\-.\+]+)_id.*",
            re.findall(r"[a-zA-Z0-9_.\+-]+.log", filename)[0],
            re.MULTILINE).groups()[0]
        feature_list['apps'] = re.match(
            r"([a-zA-Z0-9\+]*)_([a-zA-Z0-9_\-.\+]+)_id.*",
            re.findall(r"[a-zA-Z0-9_.\+-]+.log", filename)[0],
            re.MULTILINE).groups()[1]
    except:
        feature_list['users'] = "unknown"
        feature_list['apps'] = re.match(
            r"([a-zA-Z0-9\+]*).*",
            re.findall(r"[a-zA-Z0-9_.\+-]+.log", filename)[0],
            re.MULTILINE).groups()[0]

    feature_list['apps_short'] = re.match(
            r"([a-zA-Z0-9]+).*", feature_list['apps'])
    if feature_list['apps_short'] is not None:
        feature_list['apps_short'] = feature_list['apps_short'].groups(1)[0]
    else:
        feature_list['apps_short'] = ""
    return feature_list

def metadata_features(darshan_file):
    metadata, ioIndex = read_metadata(darshan_file)
    feature_list = {}
    # Extract basic information
    feature_list["Total_procs"] = int(metadata["nprocs"][0])
    feature_list["RAW_runtime"] = int(metadata["run time"][0])

    # Extract application name and user from the filename
    feature_list.update(metadata_filename(darshan_file))

    # Extract information provided by the --file flag
    feature_list.update(metadata_rw_bytes(metadata, ioIndex))
    feature_list.update(metadata_unique_bytes(metadata, ioIndex))

    # Extract information provided by the --file flag
    feature_list.update(metadata_rw_files(metadata, ioIndex))
    feature_list.update(metadata_unique_files(metadata, ioIndex))
    return feature_list
