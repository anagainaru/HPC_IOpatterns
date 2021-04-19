#  Created on: Feb 9, 2021
#      Author: Ana Gainaru gainarua@ornl.gov
# Script to extract and gather features from the aggregated darshan log
# -- only for POSIX, HDF5 and MPI-IO --

import pandas as pd

def performance_features(df, IOtype):
    type_op = ["READ", "WRITE"]
    minperf = {}
    for op in type_op:
        df_time = df[(df.Counter == "%s_F_MAX_%s_TIME" %(IOtype, op)) &\
                     (df.Value > 0)]
        df_size = df[(df.Counter == "%s_MAX_%s_TIME_SIZE" %(IOtype, op)) &\
                     (df.Value > 0)]

        fast_recordid = df_time['RecordID'].unique()
        if len(fast_recordid) == 0:
            return 0
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

def file_features(df, IOtype):
    feature_list = {}
    feature_list["%s_IO_total_files" %(IOtype)] = len(
            df[df.Counter.str.contains(IOtype)]["File"].unique())
    feature_list["%s_opens_per_file" %(IOtype)] = \
            df[(df.Counter.str.contains("OPENS")) & \
            (df.Counter.str.contains(IOtype))]["Value"].sum() /\
            feature_list["%s_IO_total_files" %(IOtype)]
    return feature_list

def _convert(df, IOtype, op_list, total_access):
    feature_list = {}
    for op in op_list:
        total_access_type = total_access
        if "SIZE_READ" in op:
            total_access_type = total_accesses(df, IOtype, type_op=['READS'])
        if "SIZE_WRITE" in op:
            total_access_type = total_accesses(df, IOtype, type_op=['WRITES'])
        feature_list[op+"_PERC"] = df[df.Counter == op]["Value"].sum() /\
                                total_access_type
    return feature_list

def convert_counters_in_perc(df, total_access, IOtype, agg="AGG_"):
    feature_list = {}
    specific_counters = {}
    specific_counters["POSIX"] = ["POSIX_WRITES", "POSIX_READS",
                                  "POSIX_FILE_NOT_ALIGNED",
                                  "POSIX_MEM_NOT_ALIGNED",
                                  "POSIX_SEQ_READS",
                                  "POSIX_SEQ_WRITES",
                                  "POSIX_CONSEC_READS",
                                  "POSIX_CONSEC_WRITES"]
    specific_counters["MPIIO"] = ["MPIIO_INDEP_READS",
                                 "MPIIO_INDEP_WRITES",
                                 "MPIIO_COLL_READS",
                                 "MPIIO_COLL_WRITES",
                                 "MPIIO_SPLIT_READS",
                                 "MPIIO_SPLIT_WRITES",
                                 "MPIIO_NB_READS",
                                 "MPIIO_NB_WRITES"]
    specific_counters["HDF5"] = ["H5D_REGULAR_HYPERSLAB_SELECTS",
                                 "H5D_IRREGULAR_HYPERSLAB_SELECTS",
                                 "H5D_POINT_SELECTS"]
    feature_list.update(
            _convert(df, IOtype, specific_counters[IOtype], total_access))

    type_op = ["%s_RW_SWITCHES" %(IOtype),
            "%s_SIZE_READ_%s0_100" %(IOtype, agg),
            "%s_SIZE_READ_%s100_1K" %(IOtype, agg),
            "%s_SIZE_READ_%s1K_10K" %(IOtype, agg),
            "%s_SIZE_READ_%s10K_100K" %(IOtype, agg),
            "%s_SIZE_READ_%s100K_1M" %(IOtype, agg),
            "%s_SIZE_READ_%s1M_4M" %(IOtype, agg),
            "%s_SIZE_READ_%s4M_10M" %(IOtype, agg),
            "%s_SIZE_READ_%s10M_100M" %(IOtype, agg),
            "%s_SIZE_READ_%s100M_1G" %(IOtype, agg),
            "%s_SIZE_READ_%s1G_PLUS" %(IOtype, agg),
            "%s_SIZE_WRITE_%s0_100" %(IOtype, agg),
            "%s_SIZE_WRITE_%s100_1K" %(IOtype, agg),
            "%s_SIZE_WRITE_%s1K_10K" %(IOtype, agg),
            "%s_SIZE_WRITE_%s10K_100K" %(IOtype, agg),
            "%s_SIZE_WRITE_%s100K_1M" %(IOtype, agg),
            "%s_SIZE_WRITE_%s1M_4M" %(IOtype, agg),
            "%s_SIZE_WRITE_%s4M_10M" %(IOtype, agg),
            "%s_SIZE_WRITE_%s10M_100M" %(IOtype, agg),
            "%s_SIZE_WRITE_%s100M_1G" %(IOtype, agg),
            "%s_SIZE_WRITE_%s1G_PLUS" %(IOtype, agg),
            "%s_ACCESS1_COUNT" %(IOtype), "%s_ACCESS2_COUNT" %(IOtype),
            "%s_ACCESS3_COUNT" %(IOtype), "%s_ACCESS4_COUNT" %(IOtype)]
    feature_list.update(
            _convert(df, IOtype, type_op, total_access))

    # raw counters
    type_op_raw = ["%s_F_VARIANCE_RANK_TIME" %(IOtype),
                   "%s_F_VARIANCE_RANK_BYTES" %(IOtype)]
    for op_raw in type_op_raw:
        feature_list[op_raw] = df[df.Counter == op_raw]["Value"].max()

    return feature_list

def RW_features(df, total_bytes, IOtype):
    feature_list = {}
    type_ops = ["READ", "WRITTEN"]
    for op in type_ops:
        feature_list["%s_BYTES_%s_PERC" %(IOtype, op)] = \
                df[df.Counter == "%s_BYTES_%s" %(IOtype, op)]["Value"].sum() /\
                total_bytes
    return feature_list

def total_other_accesses(df, IOtype, type_op):
    total_ops = 0
    for op in type_op:
        total_ops += df[(df.Counter == "%s_%s" %(IOtype, op))]["Value"].sum()
    return total_ops

def total_MPIIO_accesses(df, type_op):
    total_ops = 0
    for op in type_op:
        total_ops += df[(df.Counter.str.contains("MPIIO")) & \
                (df.Counter.str.contains(op))]["Value"].sum()
    return total_ops

def total_accesses(df, IOtype, type_op=['READS', 'WRITES']):
    if IOtype == "MPIIO":
        return total_MPIIO_accesses(df, type_op)
    return total_other_accesses(df, IOtype, type_op)

def read_aggregated_log(darshan_file):
    # Darshan files have the following format:
    # <module> <rank> <record id> <counter> <value>
    # <file name> <mount pt> <fs type>
    df = pd.read_csv(darshan_file, delimiter='\t', comment='#',
                     names=['IOType', 'Rank', 'RecordID', 'Counter', 'Value',
                            'File', 'MountPt', 'FSType'])
    # Remove entries that don't have values or are invalid
    #df = df[df.Value > 0]
    df["Rank"] = pd.to_numeric(df["Rank"])
    #df = df[not np.isnan(df.Value)]
    #df = df[(df.IOType.str.contains("POSIX")) || (df.IOType.str.contains("MPIIO"))]
    return df

def overall_features(df, IOtype, total_runtime):
    feature_list = {}
    feature_list["%s_IO_total_bytes" %(IOtype)] = \
            df[df.Counter.str.contains("%s_BYTES_" %(IOtype))]["Value"].sum()
    feature_list["%s_IO_total_accesses" %(IOtype)] = total_accesses(df, IOtype)
    feature_list["%s_read_runtime_perc" %(IOtype)] = \
            df[df.Counter == "%s_F_READ_TIME" %(IOtype)]["Value"].sum()
    feature_list["%s_write_runtime_perc" %(IOtype)] = \
            df[df.Counter == "%s_F_WRITE_TIME" %(IOtype)]["Value"].sum()
    feature_list["%s_metadata_runtime_perc" %(IOtype)] = \
            df[df.Counter == "%s_F_META_TIME" %(IOtype)]["Value"].sum()
    feature_list["%s_IO_runtime_perc" %(IOtype)] = \
            feature_list["%s_read_runtime_perc" %(IOtype)] + \
            feature_list["%s_write_runtime_perc" %(IOtype)] + \
            feature_list["%s_metadata_runtime_perc" %(IOtype)]

    # normalize the total runtime
    feature_list["%s_IO_window_perc" %(IOtype)] = \
            df[df.Counter == "%s_F_CLOSE_END_TIMESTAMP" %(IOtype)]["Value"].max() -\
            df[df.Counter == "%s_F_OPEN_START_TIMESTAMP" %(IOtype)]["Value"].min()
    feature_list["%s_IO_window_perc" %(IOtype)] /= total_runtime
    return feature_list

def additional_MPIIO_features(df, total_files):
    feature_list = {}
    feature_list["MPIIO_HINTS"] = \
            df[df.Counter=="MPIIO_HINTS"]["Value"].sum() / total_files
    feature_list["MPIIO_VIEWS"] = \
            df[df.Counter=="MPIIO_VIEWS"]["Value"].sum() / total_files
    return feature_list

def rank_features(df, IOtype):
    feature_list = {}
    IOtypeREAD = df[(df.Counter.str.contains(IOtype)) &
                    (df.Counter.str.contains("READ"))]["Rank"].unique()
    IOtypeWRITE = df[(df.Counter.str.contains(IOtype)) &
                     (df.Counter.str.contains("WRITE"))]["Rank"].unique()
    feature_list[IOtype + "_read_ranks_perc"] = len(IOtypeREAD)
    feature_list[IOtype + "_write_ranks_perc"] = len(IOtypeWRITE)
    return feature_list

def aggregated_features(darshan_file, IOtype_list, total_runtime):
    df = read_aggregated_log(darshan_file)
    feature_list = {}
    feature_list["IO_ranks"] = len(df[df.Rank >= 0]["Rank"].unique())
    for IOtype in IOtype_list:
        feature_list.update(overall_features(df, IOtype, total_runtime))
        feature_list.update(file_features(df, IOtype))
        feature_list.update(RW_features(
            df, feature_list["%s_IO_total_bytes" %(IOtype)], IOtype))

        feature_list["%s_IO_agg_perf_by_slowest" %(IOtype)] = performance_features(
                df, IOtype)

        agg = "AGG_"
        if IOtype == "POSIX":
            agg = ""
        feature_list.update(convert_counters_in_perc(
            df, feature_list["%s_IO_total_accesses" %(IOtype)], IOtype, agg=agg))

        feature_list.update(rank_features(df, IOtype))

    if "MPIIO" in IOtype_list:
        feature_list.update(additional_MPIIO_features(
            df, feature_list["MPIIO_IO_total_files"]))
    # complete the IOtype list, the metadata only knows about MPIIO and HDF5
    IOtype_used = []
    if len(df[df.File.str.startswith("/gpfs/alpine")]) > 0:
        IOtype_used.append("ALPINE")
    if len(df[df.File.str.startswith("/bb")]) > 0:
        IOtype_used.append("BB")
    if len(df[df.File.str.endswith("/md.0")]) > 0:
        IOtype_used.append("ADIOS")
    return feature_list, IOtype_used
