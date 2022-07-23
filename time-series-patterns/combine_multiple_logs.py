import json
import numpy as np
import sys
import os

from split_log_in_multiple import split_log

def update_range(value, base, current):
    scale = (base[1] - base[0]) / (current[1] - current[0])
    return int((value - current[0]) * scale + base[0])

# Read the json file and update timestamp
def read_json_data(file_name, base_ts, current_pid, outf):
    inf = open(file_name, "r")
    json_data = json.load(inf)
    min_ts = min(entry["ts"] for entry in json_data)
    max_ts = max(entry["ts"] for entry in json_data)
    if base_ts[0] == 0:
        base_ts = [min_ts, max_ts]
    # shift all the entries in json to have a min in the base timestamp
    for entry in json_data:
        # update the timestamp
        entry["ts"] = update_range(entry["ts"], base_ts, [min_ts, max_ts])
        entry["pid"] = current_pid
    inf.close()
    outf.write(',\n'.join(json.dumps(i) for i in json_data))
    return base_ts

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: %s output_file [list of logs to be merged]" %(
            sys.argv[0]))
        exit(1)

    output_file = sys.argv[1]
    try:
        os.remove(output_file)
    except:
        print("Output file", output_file)
    outf = open(output_file, 'a')
    outf.write('[\n')
    base_ts = [0, 0]
    current_pid = 0
    for file_name in sys.argv[2:]:
        base_ts = read_json_data(file_name, base_ts, current_pid, outf)
        current_pid += 1
        if len(sys.argv)-2 == current_pid:
            outf.write('\n')
        else:
            outf.write(',\n')
        print(file_name)
    outf.write(']\n')
    outf.close()
    # create the individual logs for each rank
    # in the same folder as the output file
    idx = output_file.rfind("/")
    split_log(output_file, output_file[:idx])
