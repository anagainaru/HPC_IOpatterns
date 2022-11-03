import sys
import glob

def print_usage():
    print("Usage: python %s csv_files_pattern fix/remove [save_name]" %(
        sys.argv[0]))
    print('Example submission: $ python merge_feature_files.py "summit_2021_featuresm*.csv" fix output.csv')
    print("fix/remove: entries that do not fit the pattern given in the header will be removed or fixed (by truncation)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print_usage()
        exit()
    
    if sys.argv[2]!="fix" and sys.argv[2]!="remove":
        print("Invalid parameter for the second argument, received",sys.argv[2])
        print_usage()
        exit()

    print_header=1
    outfile = "output.csv"
    if len(sys.argv) > 3:
        outfile = sys.argv[3]

    outf = open(outfile, "w")
    total_lines = 0
    for filename in glob.glob(sys.argv[1]):
        print(filename)
        inf = open(filename, "r")
        current_lines = 0
        for line in inf:
            line = line[:-1].split(",")
            if line[0]=="Total_procs" and print_header==0:
                continue
            if len(line) > 195:
                if sys.argv[2] == "fix":
                    print("WARNING ! File %s truncated from %d to 195 columns" %(
                        filename, len(line)))
                    line = line[:195]
                else:
                    print("WARNING ! Remove line with %d entries from file %s" %(
                        len(line), filename))
                    continue
            outf.write(",".join(line)+"\n")
            print_header=0
            current_lines += 1
        total_lines += current_lines
        print("Lines for file %s: %d" %(filename, current_lines))
    print("Total lines:", total_lines)
    print("Output written in", outfile)
