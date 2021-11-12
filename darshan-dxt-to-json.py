import sys
import json
import numpy as np

# Code to convert a darhan DXT log (generated with darshan-dxt-parser)
# into JSON format similar to what TAU is generating
# Example output line: {"ts": 1636314412327888, "dur": 22, "ph": "X",
    # "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "write",
    # "args": {"fd": 14, "buf": "0x7ffe02634c44", "count": 4 },
    # "pathname": "pipe", "return": 4},

# Parse metadata lines and populate additional information 
# Example lines:
# DXT, file_id: 3896614142588437040, file_name: ... 
# DXT, rank: 0, hostname: b14n17
# DXT, write_count: 1, read_count: 0
# DXT, mnt_pt: /gpfs/alpine, fs_type: gpfs
def get_metadata(line):
    data = {}
    for i in range(2, len(line), 2):
        if "count" in line[i]:
            continue
        elif line[i] == "rank":
            data["pid"] = line[i+1]
        elif line[i] == "file_id":
            data["fd"] = line[i+1]
        else:
            data[line[i]] = line[i+1]
    return data

# Return the header for the I/O information
# Example line: 
# Module	Rank	Wt/Rd	Segment	Offset	Length	Start(s)	End(s)
def get_header(line):
    header = np.array(line[1:])
    header = np.where(header == "Module", "cat", header)
    header = np.where(header == "Rank", "pid", header)
    header = np.where(header == "Wt/Rd", "name", header)
    header = np.where(header == "Start(s)", "ts", header)
    header = np.where(header == "End(s)", "dur", header)
    return header

# Populate the header with values for each I/O measurement
# X_POSIX	0	read	0	0	1928	0.0546	0.0546
def get_io_information(line, header):
    log_entry = {header[i]: line[i] for i in range(len(header))}
    # update the duration (allow min duration of 1 second)
    log_entry["ts"] = int(float(log_entry["ts"]) * (10**6)) # from seconds to us
    log_entry["dur"] = float(log_entry["dur"]) - float(log_entry["ts"])
    log_entry["dur"] = max(1, int(float(log_entry["dur"]) * (10**6))) # from seconds to us
    log_entry["pid"] = int(log_entry["pid"])
    return log_entry

# Reorganize data in the log between main features and args
# and dump the json to stdout (everything except ts, name, dur,
# tid, pid, step, cat will be in args)
def json_format(log_entry):
    if "tid" not in log_entry:
        log_entry["tid"] = 0
    if "ph" not in log_entry:
        log_entry["ph"] = "X"
    outside_info = set(["ts", "pid", "tid", "name", "dur", "ph", "cat"])
    args_info = set(log_entry.keys()) - outside_info
    log_entry_processed = {i: log_entry[i] for i in outside_info if i in log_entry}
    args = {i: log_entry[i] for i in args_info if i in log_entry}
    log_entry_processed["args"] = args
    return log_entry_processed

def main():
    if len(sys.argv) < 2:
        print("Usage: %s darshan_log_file" %(sys.argv[0]))
        return

    filename = sys.argv[1]
    inf = open(filename, "r")
    log = []
    header = []
    metadata = {}
    for line in inf:
        line = line[:-1].replace("\t", " ")
        line = line.split(" ")
        line = [i for i in line if i!=""]
        if len(line) < 2:
            continue
        if line[1] == "DXT,":
            metadata.update(get_metadata(line))
        elif line[1] == "Module":
            header = get_header(line)
        elif line[0] != "#":
            current = get_io_information(line, header)
            current.update(metadata)
            log.append(json_format(current))
            metadata = {}
    inf.close()
    print("[")
    for i in range(len(log)):
        print("%s," %(json.dumps(log[i])))
    print(json.dumps(log[len(log) - 1]))
    print("]")

if __name__ == "__main__":
    main()
