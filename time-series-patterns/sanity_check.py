import json
import numpy as np
import sys
import os

op_list = ["open", "close", "read", "write", "seek"]
sanity = 0

# Detect the file that is being used by the I/O operation
def detect_path(entry):
    path = ""
    if "args" in entry and "pathname" in entry["args"]:
        path = entry["args"]["pathname"]
    if "args" in entry and "path" in entry["args"]:
        path = entry["args"]["path"]
    if "pathname" in entry:
        path = entry["pathname"]
    if "path" in entry:
        path = entry["path"]
    if path == "pipe" or path == "socket":
        return ""
    # if the path starts with ./ remove it
    if path[:2] == "./":
        path = path[2:]
    return path

# Detect the type of operation from the list of possible operations
def detect_type_operation(entry):
    name = entry["name"]
    path = ""
    if "args" in entry and "pathname" in entry["args"]:
        path = entry["args"]["pathname"]
    for op in op_list:
        if op in name:
            return op
    if "print" in name:
        if name == "printf":
            return "stdout"
        if "std" in path: # stdin, stderr
            return "stdout"
        return "write"
    if "scan" in name: 
        if name == "scanf":
            return "stdout"
        if "std" in path: # stdin, stderr
            return "stdout"
        return "read"
    return "none"

# reutrn the path and operation type for I/O operations
# return empry string if the operation is not an I/O operation
# in case of a file name violation, return "sanity_remove" op type
def detect_path_and_optype(entry):
    global sanity
    op_type = detect_type_operation(entry)
    # only check sanity for I/O operations
    if op_type not in op_list:
        return "", ""
    path = detect_path(entry)
    if path == "": # do not save entries for unnamed files
        print("Warning ! Illegal file name for %s" %(entry))
        sanity += 1
        return "sanity_remove", ""
    if path == "stderr" or path == "stdout":
        return "", ""
    return op_type, path

# Check for violations of consecutive opens without a close in between
# Update the list of currently open files
def double_open_violations(path, current_open, entry):
    global sanity
    if path in current_open:
        print("Warning ! %s opened twice" %(path))
        sanity +=1
        return current_open, 1
    current_open[path] =[entry]
    return current_open, 0

# Check for violations of Read/Write/Close operations without a existing open
# Update the list of current open in case the operation is a close
def no_open_access_violation(op_type, current_open, path, entry):
    global sanity
    if path not in current_open:
        print("Warning ! There is a %s before open for %s" %(op_type, path))
        sanity += 1
        return current_open, 1
    # if the operation is a close operation, remove file from the open list
    if op_type == "close":
        del current_open[path]
    else: # for all other operations keep track of all entries
        current_open[path].append(entry)
    return current_open, 0

# Check violations for files opened but not closed
def dangling_open_violations(current_open, remove):
    global sanity
    if len(current_open) == 0:
        return remove
    # remaining entries are opens that were not closed
    for path in current_open:
        print("Warning ! %s was opened but not closed" %(path))
        sanity += 1
        for idx in current_open[path]:
            remove.append(idx)
    return remove

# Write the existing log to an output file
def write_log_to_json(json_data, out_file, move=[]):
    outf = open(out_file, 'w')
    outf.write('[\n')
    outf.write(',\n'.join(json.dumps(i) for i in json_data))
    outf.write('\n]\n')
    outf.close()

# Function to delete all entries that violate the access order of
# I/O operations
def delete_violations(json_data, out_file=""):
    remove = []
    current_open = {} # for each path: [index list] of open and all following R/W
    for i in range(len(json_data)):
        entry = json_data[i]
        op_type, path = detect_path_and_optype(entry)
        if op_type == "":
            continue
        if op_type == "sanity_remove":
            remove.append(i)
            continue
        # store open operations
        if op_type == "open":
            current_open, check = double_open_violations(
                    path, current_open, i)
            if check == 1: # violation for double open
                remove.append(i)
            continue
        current_open, check = no_open_access_violation(
                op_type, current_open, path, i)
        if check == 1: # violations during close, read or write
            remove.append(i)
    # check violations for open without a close
    remove = dangling_open_violations(current_open, remove)
    remove.sort(reverse=True)
    print("%d violations found. Removing %d entries." %(sanity, len(remove)))
    for i in remove:
        del json_data[i]
    if out_file != "":
        write_log_to_json(json_data, out_file)
    return json_data

# There are R/W/close operations for which the file has been closed
# Fix the violation by removing the last close operation
def no_open_access_fix(path, op_type, last_close,
                              check, entry):
    remove = -1
    # if a violation has occured, remove the last close
    # unless it has already been removed by a previous violation
    # e.g. O C W R C only the first W will remove the second C
    if check == 1 and last_close[1] != -1:
        remove = last_close[1]
        last_close[2] = last_close[1]
        last_close[1] = -1
    # if the current operation is a close
    # keep track of the latest pair of open - close operations
    if op_type == "close":
        last_close[2] = entry
        last_close[1] = entry
    return remove, last_close

# Fix violations for files opened but not closed
# by moving an exisitng close at the end of the log
def dangling_open_fix(current_open, last_close):
    global sanity
    remove = []
    add = []
    if len(current_open) == 0:
        return remove, add
    # remaining entries are opens that were not closed
    for path in current_open:
        print("Warning ! %s was opened but not closed" %(path))
        sanity += 1
        if path in last_close and last_close[path][2] != -1:
            add.append(last_close[path][2])
        else:
            for idx in current_open[path]:
                remove.append(idx)
    return remove, add

# Attempt to correct the violations
def correct_violations(json_data, out_file=""):
    remove = []
    current_open = {} # for each path: [index list] of open and all following R/W
    last_close = {}   # for each path: (open, close index, last deleted close index)
    for i in range(len(json_data)):
        entry = json_data[i]
        # illegal paths will be removed
        op_type, path = detect_path_and_optype(entry)
        if op_type == "":
            continue
        if op_type == "sanity_remove":
            remove.append(i)
            continue

        # double open violations will delete the second
        if op_type == "open":
            current_open, check = double_open_violations(
                    path, current_open, i)
            if check == 1: # violation for double open
                remove.append(i)
            else:
                # save the last open for each file
                last_close[path] = [i, -1, -1]
            continue

        current_open, check = no_open_access_violation(
                op_type, current_open, path, i)
        # R/W/close will be removed if there is no intitial open
        if check == 1 and path not in last_close: 
            remove.append(i)
            continue
        # otherwise delete the close that made the open inactive
        remove_entry, last_close[path] = no_open_access_fix(
                path, op_type, last_close[path], check, i)
        if remove_entry != -1:
            remove.append(remove_entry)
            current_open[path] = [last_close[path][0]]
    # open without close will aim to find a previous close and copy it
    # with a timestamp of the last entry in the open list + 1
    # if dangling violation, if path not in close, we remove all the entries in the open list
    # if path is in close, we add an entry from the close index and update the timestamp
    remove_entry, add_entry = dangling_open_fix(current_open, last_close)
    remove += remove_entry
    remove = list(set(remove) - set(add_entry))
    print(remove_entry, add_entry)
    print("Remove list", remove)
    print("Current open list", current_open)
    print("Last close", last_close)
    remove.sort(reverse=True)
    print("%d violations found. Removing %d entries." %(sanity, len(remove)))
    for i in remove:
        del json_data[i]
    if out_file != "":
        write_log_to_json(json_data, out_file, move=add_entry)
    return json_data

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s input_json" %(
            sys.argv[0]))
        exit(1)
    json_file = sys.argv[1]
    inf = open(json_file, "r")
    json_data = json.load(inf)
    #delete_violations(json_data, "test/clean.json")
    correct_violations(json_data, "test/clean.json")
    inf.close()
