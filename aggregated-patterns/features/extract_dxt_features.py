# Script to extract and gather features from the DXT darshan log
# -- only for POSIX --
import pandas as pd
import re

def get_accessed_files(file):
    inf = open(file)
    file_list = []
    cfile = 0
    for line in inf:
        if "DXT, file_id:" in line:
            idx = line.find("file_name")
            cfile = line[idx+11:-1]
        if "DXT, write_count:" in line:
            access_cnt = sum([int(i) for i in re.findall(r'\d+', line)])
            file_list += [cfile] * access_cnt
    inf.close()
    return file_list

def read_dxt_logs(darshan_file):
    df = pd.read_csv(darshan_file, delimiter='\t', comment='#',
                     names=["Module", "Rank", "IOType", "Segment", "Offset",
                            "Length", "Start", "End"])
    # Additional information to help extract features
    df["File"] = get_accessed_files(darshan_file)
    df["Offset_end"] = df["Offset"] + df["Length"]

    # Filter out entries with length 0
    df = df[df.Length > 0]
    return df

def consecutive_RW(df):
    feature_list = {}
    # Read after write (percentage of reads after write to total reads)
    # group is true if consecutive entries belong to the same file
    #   and the two consecutive entries are write / read
    df['group'] = (df['IOType'] == "write") & \
            (df['IOType'].shift(1) == "read") & \
            (df['File'] == df['File'].shift(1))
    allReads = len(df[df.IOType == "read"])
    feature_list["READ_after_WRITE_PERC"] = \
            len(df[df.group == True]) / allReads

    # Read after read
    df['group'] = (df['IOType'] == "read") & \
            (df['IOType'].shift(1) == "read") & \
            (df['File'] == df['File'].shift(1))
    feature_list["READ_after_READ_PERC"] = \
            len(df[df.group == True]) / allReads

    # Write after read
    df['group'] = (df['IOType'] == "read") & \
            (df['IOType'].shift(1) == "write") & \
            (df['File'] == df['File'].shift(1))
    allWrites = len(df[df.IOType == "write"])
    feature_list["WRITE_after_READ_PERC"] = \
            len(df[df.group == True]) / allWrites

    # Write after write
    df['group'] = (df['IOType'] == "write") & \
            (df['IOType'].shift(1) == "write") & \
            (df['File'] == df['File'].shift(1))
    feature_list["WRITE_after_WRITE_PERC"] = \
            len(df[df.group == True]) / allWrites

    # RAW + RAR is not equal to 1 because the first read of each file 
    #   are not counted toward either
    return feature_list

def rank_features(total_rw, total_IO_ranks, total_files, total_accesses):
    feature_list = {}
    # consecutive memory accesses to the same file by the same rank
    df['group'] = (df['Rank'] == df['Rank'].shift(1)) & \
            (df['File'] == df['File'].shift(1))
    feature_list["Rank_consecutive_perc"] = \
            len(df[df.group == True]) / total_accesses

    # consecutive memory accesses to the same file by the different ranks
    df['group'] = (df['Rank'] != df['Rank'].shift(1)) & \
            (df['File'] == df['File'].shift(1))
    feature_list["Rank_switches_perc"] = \
            len(df[df.group == True]) / total_accesses

    # ranks doing only read, only write
    temp = df.groupby('Rank')['IOType'].unique()
    feature_list["Ranks_read_write_perc"] = len([i for i in temp if len(i)==2])
    feature_list["Ranks_read_only_perc"] = len([i for i in temp if len(i)==1
                                           and i[0]=="read"])
    feature_list["Ranks_write_only_perc"] = len([i for i in temp if len(i)==1
                                            and i[0]=="write"])
    # normalize the metrics
    feature_list["Ranks_read_write_perc"] /= total_IO_ranks
    feature_list["Ranks_read_only_perc"] /= total_IO_ranks
    feature_list["Ranks_write_only_perc"] /= total_IO_ranks

    # percentage files accessed  by ony one rank
    temp = df.groupby('File')['Rank'].unique()
    feature_list["File_one_rank_perc"] = len([i for i in temp if len(i)==1])
    feature_list["File_multiple_ranks_perc"] = \
            len([i for i in temp if len(i)>1])
    # normalize features
    feature_list["File_one_rank_perc"] /= total_files
    feature_list["File_multiple_ranks_perc"] /= total_files
    return feature_list

def dxt_features(darshan_file):
    df = read_dxt_logs(darshan_file)

    total_IO_ranks = len(df["Rank"].unique())
    total_files = len(df["File"].unique())
    total_accesses = len(df)

    feature_list = {}
    print("DXT", total_accesses, total_IO_ranks, total_files)
    # add RAW/WAR/.. information
    feature_list.update(consecutive_RW(df))
    feature_list.update(rank_features(df, total_IO_ranks, total_files, total_accesses))
    return feature_list
