import json
import numpy as np
import sys

def read_json_data(file_name):
    inf = open(file_name, "r")
    json_data = json.load(inf)
    separate_data = {}
    for entry in json_data:
        if entry["pid"] not in separate_data:
            separate_data[entry["pid"]] = []
        separate_data[entry["pid"]].append(entry)
    inf.close()
    return separate_data

def split_log(input_file, output_path):
    log = read_json_data(input_file)
    for rank in log:
        outf = open(output_path+'/rank'+'{:05}'.format(rank)+'.trace.json', 'w')
        outf.write('[\n')
        outf.write(',\n'.join(json.dumps(i) for i in log[rank]))
        outf.write('\n]\n')
        outf.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: %s aggregate_file output_folder" %(
            sys.argv[0]))
        exit(1)

    input_file = sys.argv[1]
    output_path = sys.argv[2]
    split_log(input_file, output_path)
