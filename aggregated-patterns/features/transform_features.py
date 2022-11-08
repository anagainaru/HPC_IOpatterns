import sys
import numpy as np
import pandas as pd
import seaborn as sns; sns.set()
import matplotlib.pyplot as plt
import os, glob

type_of_features = "bin" # or continuous

# applications using storage options: ALPINE, BB
def conditions_storage(df):
    if (df.is_ALPINE == 1) & (df.is_BB == 1):
        return 3
    if (df.is_ALPINE == 0) & (df.is_BB == 0):
        return 2
    if (df.is_ALPINE == 1):
        return 0
    return 1

# applications using IO libraries: ADIOS, HDF5, MPIIO
def conditions_library(df):
    if (df.is_ADIOS == 1) & (df.is_HDF5 == 0) & (df.is_MPIIO == 0):
        return 1
    if (df.is_ADIOS == 0) & (df.is_HDF5 == 1) & (df.is_MPIIO == 0):
        return 2
    if (df.is_ADIOS == 0) & (df.is_HDF5 == 0) & (df.is_MPIIO == 1):
        return 3
    if (df.is_ADIOS == 0) & (df.is_HDF5 == 0) & (df.is_MPIIO == 0):
        return 0
    return 4

def extract_basic_info(df):
    out_df = pd.DataFrame()
    out_df["user"] = df["user"]
    out_df["exec_name"] = df["exec_name"]
    out_df["app_name"] = df["app_name"]
    out_df = out_df.assign(storage = df.apply(conditions_storage, axis=1))
    out_df = out_df.assign(IO_library = df.apply(conditions_library, axis=1))
    return out_df

# transform the features related to metadata
def conditions_open(df):
    if (df.POSIX_opens_per_file <= 1) & (df.MPIIO_opens_per_file <= 1) & (df.HDF5_opens_per_file <= 1):
        return 0 # only one open per file
    if 3*df.Total_opens < df.Total_accesses:
        return 1 # Few opens compared to accesses
    return 2 # Heavy on opens

def extract_metadata(df, out_df):
    df["Metadata_perc"] = df.Metadata_runtime / (df.IO_runtime + df.Metadata_runtime)
    if type_of_features == "bin":
        out_df.loc[df.Metadata_perc < 0.25, "metadata"] = 0
        out_df.loc[df.Metadata_perc >= 0.25, "metadata"] = 1
    else:
        out_df["metadata"] = np.minimum(1,df["Metadata_perc"])
    df["IO_intensive"] = df.IO_runtime / (df.Total_runtime + df.IO_runtime)
    if type_of_features == "bin":
        out_df.loc[df.IO_intensive < 0.25, "IO_intensive"] = 0
        out_df.loc[df.IO_intensive >= 0.25, "IO_intensive"] = 1
    else:
        out_df["IO_intensive"] = np.minimum(1,df["IO_intensive"])
    df["Total_opens"] = (df["POSIX_opens_per_file"] + df["MPIIO_opens_per_file"] + df["HDF5_opens_per_file"]) *\
                        (df["POSIX_IO_total_files"] + df["MPIIO_IO_total_files"] + df["HDF5_IO_total_files"])
    df["Total_accesses"] = df["POSIX_IO_total_accesses"]+df["MPIIO_IO_total_accesses"]+df["HDF5_IO_total_accesses"]
    df["Total_accesses"] += df["Total_opens"]
    df = df[df.Total_accesses > 0]

    if type_of_features == "bin":
        out_df = out_df.assign(open_access = df.apply(conditions_open, axis=1))
    else:
        out_df["open_access"] = np.minimum(1,df["Total_opens"]/df["Total_accesses"])
    return out_df

# transform the features related to the amount of IO performed
def conditions_intensive_IO(df):
    if df.RW_coef < -0.5: # write intensive
        return 2
    if (df.RW_coef >= -0.5) & (df.RW_coef < 0.5):
        return 1
    return 0 # read intensive

def extract_amount_IO(df, out_df):
    df["RW_coef"] = (df.Total_bytes_READ - df.Total_bytes_WRITTEN) / (df.Total_bytes_READ + df.Total_bytes_WRITTEN)
    if type_of_features == "bin":
        out_df = out_df.assign(RW_intensive=df.apply(conditions_intensive_IO, axis=1))
    else:
        out_df["RW_intensive"] = np.maximum(-1, np.minimum(1,df["RW_coef"]))
    return out_df

# transform features related to write/read accesses
def conditions_access(df, column, new_field, out_df):
    out_df.loc[df[column] < 0.25, new_field] = 1
    if type_of_features == "bin":
        out_df.loc[df[column] > 0.75, new_field] = 2
    else:
        out_df.loc[df[column] > 0.75, new_field] = -1
    out_df.loc[(df[column] >= 0.25) & (df[column] <= 0.75), new_field] = 0
    return out_df

def conditions_write_size(df):
    if (df.Total_large_WRITES == 0) & (df.Total_small_WRITES == 0): # no reads
        return 0
    if df.Total_large_WRITES == 0: # no large reads
        return 1
    if df.Total_small_WRITES == 0: # no small reads
        return 2
    if df.Total_large_WRITES > 3*df.Total_small_WRITES:
        return 3 # mostly large reads
    if df.Total_small_WRITES > 3*df.Total_large_WRITES:
        return 4 # mostly small reads
    return 5 # balanced

def conditions_read_size(df):
    if (df.Total_large_READS == 0) & (df.Total_small_READS == 0): # no reads
        return 0
    if df.Total_large_READS == 0: # no large reads
        return 1
    if df.Total_small_READS == 0: # no small reads
        return 2
    if df.Total_large_READS > 3*df.Total_small_READS:
        return 3 # mostly large reads
    if df.Total_small_READS > 3*df.Total_large_READS:
        return 4 # mostly small reads
    return 5 # balanced

def conditions_access_type(df):
    if (df.Total_read_write_bytes == 1): # only read/write accesses
        return 0
    if (df.Total_read_only_bytes == 1): # only read accesses
        return 1
    if (df.Total_write_only_bytes == 1): # only write accesses
        return 2
    if (df.Total_read_only_bytes > 0.5): # mostly read accesses
        return 3
    if (df.Total_write_only_bytes > 0.5): # mostly write accesses
        return 4
    if (df.Total_read_write_bytes > 0.5): # mostly read/write accesses
        return 5
    return 6

def extract_WR_access_patterns(df, out_df):
    # consecutive, sequential accesses
    df.loc[(df.POSIX_WRITES>0), 'Seq_WRITES_perc'] = df.POSIX_SEQ_WRITES / df.POSIX_WRITES
    df.loc[(df.POSIX_WRITES==0), 'Seq_WRITES_perc'] = 0
    df.loc[(df.POSIX_READS>0), 'Seq_READS_perc'] = df.POSIX_SEQ_READS / df.POSIX_READS
    df.loc[(df.POSIX_READS==0), 'Seq_READS_perc'] = 0
    df.loc[(df.POSIX_WRITES>0), 'Consec_WRITES_perc'] = df.POSIX_CONSEC_WRITES / df.POSIX_WRITES
    df.loc[(df.POSIX_WRITES==0), 'Consec_WRITES_perc'] = 0
    df.loc[(df.POSIX_READS>0), 'Consec_READS_perc'] = df.POSIX_CONSEC_READS / df.POSIX_READS
    df.loc[(df.POSIX_READS==0), 'Consec_READS_perc'] = 0
    out_df = conditions_access(df, "Seq_WRITES_perc", "WRITE_seq", out_df)
    out_df = conditions_access(df, "Seq_READS_perc", "READS_seq", out_df)
    out_df = conditions_access(df, "Consec_WRITES_perc", "WRITE_consec", out_df)
    out_df = conditions_access(df, "Consec_READS_perc", "READS_consec", out_df)
    
    # amount of large/small accesses
    df["Total_large_READS"] = df.filter(like='1G_PLUS').filter(like='READ').sum(axis = 1)
    df["Total_large_WRITES"] = df.filter(like='1G_PLUS').filter(like='WRITE').sum(axis = 1)
    columns = [i for i in list(df) if ('0_100' in i or '100_1K' in i or '1K_10K' in i or '10k_100k' in i 
           or '100k_1M' in i or '1M_4M' in i or '4M_10M' in i or '10M_100M' in i or '100M_1G' in i) and
           'READ' in i]
    df["Total_small_READS"] = df[columns].sum(axis = 1)
    columns = [i for i in list(df) if ('0_100' in i or '100_1K' in i or '1K_10K' in i or '10k_100k' in i 
               or '100k_1M' in i or '1M_4M' in i or '4M_10M' in i or '10M_100M' in i or '100M_1G' in i) and
               'WRITE' in i]
    df["Total_small_WRITES"] = df[columns].sum(axis = 1)
    if type_of_features == "bin":
        out_df = out_df.assign(read_access_size = df.apply(conditions_read_size, axis=1))
        out_df = out_df.assign(write_access_size = df.apply(conditions_write_size, axis=1))
    else:
        out_df["read_access_size"] = (df.Total_large_READS - df.Total_small_READS) /\
                (df.Total_large_READS + df.Total_small_READS)
        out_df["write_access_size"] = (df.Total_large_WRITES - df.Total_small_WRITES) /\
                (df.Total_large_WRITES + df.Total_small_WRITES)

    # amount of bytes that are both read and written compared to read/write only
    df["Total_read_write_bytes"] = df.filter(like='read_write_bytes').sum(axis = 1)
    df["Total_read_only_bytes"] = df.filter(like='read_only_bytes').sum(axis = 1)
    df["Total_write_only_bytes"] = df.filter(like='write_only_bytes').sum(axis = 1)
    df["Total_bytes"] = df["Total_read_write_bytes"] + df["Total_read_only_bytes"] + df["Total_write_only_bytes"]
    df["Total_read_write_bytes"] /= df["Total_bytes"]
    df["Total_read_only_bytes"] /= df["Total_bytes"]
    df["Total_write_only_bytes"] /= df["Total_bytes"]
    if type_of_features == "bin":
        out_df = out_df.assign(access_type = df.apply(conditions_access_type, axis=1))
    else:
        out_df["read_only"] = df["Total_read_only_bytes"]
        out_df["write_only"] = df["Total_write_only_bytes"]
    return out_df

# transform features related to file accesses
def conditions_access_file(df):
    if (df.Total_read_write_files == 1): # only read/write accesses
        return 0
    if (df.Total_read_only_files == 1): # only read accesses
        return 1
    if (df.Total_write_only_files == 1): # only write accesses
        return 2
    if (df.Total_read_only_files > 0.5): # mostly read accesses
        return 3
    if (df.Total_write_only_files > 0.5): # mostly write accesses
        return 4
    if (df.Total_read_write_files > 0.5): # mostly read/write accesses
        return 5
    return 6

def conditions_file_type(df):
    if (df.unique_files == 1): # only unique file accesses
        return 0
    if (df.shared_files == 1): # only shared file accesses
        return 1
    if (df.unique_files >= 0.5): # mostly unique file accesses
        return 2
    if (df.shared_files >= 0.5): # mostly shared file accesses
        return 3
    return 4

def extract_file_access(df, out_df):
    # access patterns
    df["Total_read_write_files"] = df.filter(like='read_write_files').sum(axis = 1)
    df["Total_read_only_files"] = df.filter(like='read_only_files').sum(axis = 1)
    df["Total_write_only_files"] = df.filter(like='write_only_files').sum(axis = 1)
    df["Total_files"] = df["Total_read_write_files"] + df["Total_read_only_files"] + df["Total_write_only_files"]
    df["Total_read_write_files"] /= df["Total_files"]
    df["Total_read_only_files"] /= df["Total_files"]
    df["Total_write_only_files"] /= df["Total_files"]
    if type_of_features == "bin":
        out_df = out_df.assign(file_access_type = df.apply(conditions_access_file, axis=1))
    else:
        out_df["file_read_only"] = df["Total_read_only_files"]
        out_df["file_write_only"] = df["Total_write_only_files"]

    # unique/shared files
    df["unique_files"] = df["POSIX_unique_files"]+df["MPIIO_unique_files"]+df["HDF5_unique_files"]
    df["shared_files"] = df["POSIX_shared_files"]+df["MPIIO_shared_files"]+df["HDF5_shared_files"]
    df["total_files"] = df["unique_files"] + df["shared_files"]
    df["unique_files"] /= df["total_files"]
    df["shared_files"] /= df["total_files"]
    if type_of_features == "bin":
        out_df = out_df.assign(file_type = df.apply(conditions_file_type, axis=1))
    else:
        out_df["file_type"] = (df["unique_files"] - df["shared_files"])/(df["unique_files"] + df["shared_files"])
    return out_df

# transform features related to IO accesses across ranks
def conditions_ranks(df):
    if (df.Total_IO_ranks == 1) & (df.Total_procs > 1):
        return 0 # only one rank is doing I/O
    if (df.IO_ranks == 1): # all ranks are doing I/O
        return 1
    if (df.IO_ranks >= 0.5):
        return 2 # most ranks are doing I/O
    return 3 # few ranks are doing I/O

def conditions_WR_ranks(df):
    if (df.Total_read_ranks == 1) & (df.Total_write_ranks == 1): # all ranks are doing both R and W
        return 0
    if df.Total_read_ranks == 0: # no rank is doing read
        return 1
    if df.Total_write_ranks == 0: # no rank is doing write
        return 2
    if df.Total_read_ranks > 3*df.Total_write_ranks:
        return 3 # most ranks are doing read
    if df.Total_write_ranks > 3*df.Total_read_ranks:
        return 4 # most ranks are doing write
    return 5 # balanced

def extract_rank_access(df, out_df):
    # rank access pattern
    df["Total_IO_ranks"] = df["IO_ranks"] * df["Total_procs"]
    if type_of_features == "bin":
        df["Total_read_ranks"] /= df["Total_IO_ranks"]
        df["Total_write_ranks"] /= df["Total_IO_ranks"]
        out_df = out_df.assign(ranks_IO = df.apply(conditions_ranks, axis=1))
        out_df = out_df.assign(ranks_RW = df.apply(conditions_WR_ranks, axis=1))
    else:
        out_df["ranks_IO"] = df["IO_ranks"]
        out_df["ranks_RW"] = (df["Total_read_ranks"]-df["Total_write_ranks"]) /\
                (df["Total_read_ranks"] + df["Total_write_ranks"])

    # variance
    df["max_variance"] = df[["POSIX_F_VARIANCE_RANK_BYTES", "MPIIO_F_VARIANCE_RANK_BYTES", "HDF5_F_VARIANCE_RANK_BYTES"]].max(axis = 1)
    out_df.loc[df["max_variance"] == 0, "ranks_variance"] = -1
    out_df.loc[(df["max_variance"] >0) & (df["max_variance"]<0.2), "ranks_variance"] = 0
    out_df.loc[df["max_variance"] >= 0.25, "ranks_variance"] = 1
    return out_df

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python %s csv_file header_file bin/continuous [save_name]" %(
            sys.argv[0]))
        exit()

    if sys.argv[3]!="bin" and sys.argv[3]!="continuous":
        print("Invalid option for the third argument. Expected bin or continuous")
        print("Received:", sys.argv[3])
        exit()

    type_of_features = sys.argv[3]

    # read the header file
    header = set()
    inf = open(sys.argv[2], "r")
    for line in inf:
        header.add(line[:-1])
    # Read into a dataframe all the files matching the given pattern
    df = pd.DataFrame(columns=header)
    for filename in glob.glob(sys.argv[1]):
        data = pd.read_csv(filename, delimiter=',')
        df = pd.concat([df, data])
        print("Add file:", filename)

    # filter all entries that execute for less than 5 minutes
    df = df[df.Total_runtime > 300]
    # Filter all applications that do not perform any I/O
    df["Total_bytes_READ"] = df.POSIX_BYTES_READ + df.HDF5_BYTES_READ + df.MPIIO_BYTES_READ
    df["Total_bytes_WRITTEN"] = df.POSIX_BYTES_WRITTEN + df.HDF5_BYTES_WRITTEN + df.MPIIO_BYTES_WRITTEN
    df = df[(df.Total_bytes_READ + df.Total_bytes_WRITTEN) > 0]
    print("Total entries added:", len(df))

    out_df = extract_basic_info(df)
    out_df = extract_metadata(df, out_df)
    out_df = extract_amount_IO(df, out_df)
    out_df = extract_WR_access_patterns(df, out_df)
    out_df = extract_file_access(df, out_df)
    out_df = extract_rank_access(df, out_df)
    print(out_df[["metadata", "open_access", "IO_intensive"]])

    out_df = out_df.fillna(0)
    outfile = "output_bins.cvs"
    if len(sys.argv)>4:
        outfile = sys.argv[4]
    out_df.to_csv(outfile, index=False)
    print("Output written in", outfile)
