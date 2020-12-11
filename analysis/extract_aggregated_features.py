# Script to extract and gather features from the aggregated darshan log
# -- only for POSIX --

import pandas as pd

def performance_features(df):
    type_op = ["READ", "WRITE"]
    minperf = {}
    for op in type_op:
        df_time = df[(df.Counter == "POSIX_F_MAX_%s_TIME" %(op)) &\
                     (df.Value > 0)]
        df_size = df[(df.Counter == "POSIX_MAX_%s_TIME_SIZE" %(op)) &\
                     (df.Value > 0)]

        fast_recordid = df_time['RecordID'].unique()
        perf = {}
        # For each record find the slowest I/O and compute bandwidth
        #   (one entry for the amount of bytes and time to transfer)
        for record in fast_recordid:
            # time / size
            time = df_time[(df_time.RecordID == record)]["Value"].values[0]
            size = df_size[(df_size.RecordID == record)]["Value"].values[0]
            if record not in perf:
                perf[record] = size / time
            if size / time < perf[record]:
                perf[record] = size / time
        # Only keep the minimum across all recors
        minperf[op] = min([perf[i] for i in perf])
    # Return the minimum across all I/O operations
    return min(minperf[i] for i in minperf)

def file_features(df):
    feature_list = {}
    feature_list["POSIX_RAW_total_files"] = len(df["File"].unique())
    feature_list["POSIX_RAW_OPENS"] = \
            df[df.Counter == "POSIX_OPENS"]["Value"].sum()

    # if this information was not provided in the metadata
    if "POSIX_unique_files_perc" not in feature_list: 
        # Shared files are the ones accessed by more than one rank
        temp = []
        for _, group in df[(df.Counter == "POSIX_READS") | \
                           (df.Counter == "POSIX_WRITES")].groupby("File"):
            temp.append(len(group.Rank.unique()))
        feature_list["POSIX_unique_files_perc"] = \
                len([i for i in temp if i == 1]) /\
                feature_list["POSIX_RAW_total_files"]
        feature_list["POSIX_shared_files_perc"] = \
                len([i for i in temp if i > 1]) /\
                feature_list["POSIX_RAW_total_files"]

    if "POSIX_read_write_files_perc" not in feature_list:
        # Read only files are the ones that appear in only READ operations
        write_set = set(df[df.Counter.str.contains("WRITE|WRITTEN")]
                          ["File"].unique())
        read_set = set(df[df.Counter.str.contains("READ")]["File"].unique())
        feature_list["POSIX_read_only_files_perc"] = \
                len(read_set - write_set) / len(read_set | write_set)
        feature_list["POSIX_read_write_files_perc"] = \
                len(write_set & read_set) / len(read_set | write_set)
        feature_list["POSIX_write_only_files_perc"] = \
                len(write_set - read_set) / len(read_set | write_set)
    return feature_list

def convert_counters_in_perc(df, total_access):
    feature_list = {}
    # Percentage is defined as sum of each counter over total number of accesses
    type_op = ["POSIX_WRITES_PERC",
            "POSIX_RW_SWITCHES_PERC", "POSIX_READS_PERC",
            "POSIX_FILE_NOT_ALIGNED_PERC", "POSIX_MEM_NOT_ALIGNED_PERC",
            "POSIX_SIZE_READ_0_100_PERC", "POSIX_SIZE_READ_100_1K_PERC",
            "POSIX_SIZE_READ_1K_10K_PERC", "POSIX_SIZE_READ_10K_100K_PERC",
            "POSIX_SIZE_READ_100K_1M_PERC", "POSIX_SIZE_READ_1M_4M_PERC",
            "POSIX_SIZE_READ_4M_10M_PERC", "POSIX_SIZE_READ_10M_100M_PERC",
            "POSIX_SIZE_READ_100M_1G_PERC", "POSIX_SIZE_READ_1G_PLUS_PERC",
            "POSIX_SIZE_WRITE_0_100_PERC", "POSIX_SIZE_WRITE_100_1K_PERC",
            "POSIX_SIZE_WRITE_1K_10K_PERC", "POSIX_SIZE_WRITE_10K_100K_PERC",
            "POSIX_SIZE_WRITE_100K_1M_PERC", "POSIX_SIZE_WRITE_1M_4M_PERC",
            "POSIX_SIZE_WRITE_4M_10M_PERC", "POSIX_SIZE_WRITE_10M_100M_PERC",
            "POSIX_SIZE_WRITE_100M_1G_PERC", "POSIX_SIZE_WRITE_1G_PLUS_PERC",
            "POSIX_ACCESS1_COUNT_PERC", "POSIX_ACCESS2_COUNT_PERC",
            "POSIX_ACCESS3_COUNT_PERC", "POSIX_ACCESS4_COUNT_PERC"]
    for op_perc in type_op:
        op = op_perc[:-5]
        feature_list[op_perc] = df[df.Counter == op]["Value"].sum() /\
                                total_access

    # Percentage is defined by sum of each conter over total writes/reads
    type_op = ["POSIX_SEQ_READS_PERC", "POSIX_SEQ_WRITES_PERC",
               "POSIX_CONSEC_READS_PERC", "POSIX_CONSEC_WRITES_PERC"]
    for op_perc in type_op:
        op = op_perc[:-5]
        total_access_type = df[df.Counter == "POSIX_WRITES"]["Value"].sum()
        if "READ" in op:
            total_access_type = df[df.Counter == "POSIX_READS"]["Value"].sum()
        feature_list[op_perc] = df[df.Counter == op]["Value"].sum() /\
                                total_access_type
    return feature_list

def RW_features(df, total_bytes):
    feature_list = {}
    type_ops = ["READ", "WRITTEN"]
    for op in type_ops:
        feature_list["POSIX_BYTES_%s_PERC" %(op)] = \
                df[df.Counter == "POSIX_BYTES_%s" %(op)]["Value"].sum() /\
                total_bytes
    return feature_list

def total_accesses(df):
    type_op = ['READS', 'WRITES']
    total_ops = 0
    for op in type_op:
        total_ops += df[(df.Counter == "POSIX_" + op)]["Value"].sum()
    return total_ops

def read_aggregated_log(darshan_file):
    # Darshan files have the following format:
    # <module> <rank> <record id> <counter> <value>
    # <file name> <mount pt> <fs type>
    df = pd.read_csv(darshan_file, delimiter='\t', comment='#',
                     names=['IOType', 'Rank', 'RecordID', 'Counter', 'Value',
                            'File', 'MountPt', 'FSType'])
    # Remove entries that don't have values or are invalid
    df = df[df.Value > 0]
    #df = df[not np.isnan(df.Value)]

    # only keep POSIX entries
    df = df[df.IOType.str.contains("POSIX")]
    return df

def aggregated_features(darshan_file):
    df = read_aggregated_log(darshan_file)
    print("Agg", total_accesses(df),  len(df[(df.Counter == "POSIX_READS") | \
                           (df.Counter == "POSIX_WRITES")]["Rank"].unique()))
    feature_list = {}
    feature_list["POSIX_RAW_total_bytes"] = \
            df[df.Counter.str.contains("POSIX_BYTES_")]["Value"].sum()
    feature_list["POSIX_RAW_total_accesses"] = total_accesses(df)
    
    feature_list.update(file_features(df))
    feature_list.update(RW_features(df, feature_list["POSIX_RAW_total_bytes"]))
    
    feature_list["POSIX_RAW_agg_perf_by_slowest"] = performance_features(df)
    feature_list.update(convert_counters_in_perc(
        df, feature_list["POSIX_RAW_total_accesses"]))
    return feature_list
