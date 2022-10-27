## I/O benchmark on Summit
### Running the benchmark

_Prerequisites_: A collection of TAU logs that capture the I/O of applications that will be used to create the benchmark

_Output_: An executable that can be submitted on Summit to simulate the execution of the input applications 

_Steps_: 
1. Combine multiple logs to create new patterns within one application
2. Modify existing logs to fit the simulation parameters (execution time, number of cores, etc.)
3. Combine multiple applications to create new patterns across the entire execution
4. Run the benchmark

**NOTE** - All logs can be visualized with the chrome tracer at: [chrome://tracing/](chrome://tracing/)

**1. Combine multiple logs to create new patterns within one application**

Example logs are provided in the log folder, with one folder for one application. The folders have one JSON file called `all.trace.json` containing the logs of all the rank and individual files for each rank (e.g. `rank00000.trace.json`).

```
$ ls logs/
README.md lammps warpx

$ ls logs/lammps
all.trace.json       rank00001.trace.json rank00003.trace.json rank00005.trace.json rank00007.trace.json rank00009.trace.json
rank00000.trace.json rank00002.trace.json rank00004.trace.json rank00006.trace.json rank00008.trace.json

$ cat README.md
LAMMPS: 10 ranks; execution time 1537 seconds
WarpX: 4 ranks; execution time 861 seconds
```

To combine the I/O pattern of rank 0 from LAMMPS with the I/O pattern of rank 0 from WarpX in a new hybrid application, the `combine_multiple_logs.py` script can be used.

```
$ python combine_multiple_logs.py
Usage: combine_multiple_logs.py output_file [list of logs to be merged]

$ mkdir -p hybrid
$ python combine_multiple_logs.py logs/hybrid/all.trace.json logs/lammps/rank00000.trace.json logs/warpx/rank00000.trace.json
$ ls logs/hybrid
all.trace.json 
```

<img width="688" alt="Screen Shot 2022-07-20 at 11 37 07 AM" src="https://user-images.githubusercontent.com/16229479/180024123-eb3be708-2728-441b-b46e-8d4fc148f693.png">

**2. Modify existing logs to fit the simulation parameters**

Starting from a given application log (with one or multiple ranks gathered in one json), it is possible to create a new log with longer/shorter execution time or more/less total ranks by using the extract_patterns_json.py script.

The script has many options, but in the simplest form, the script takes an input TAU log and the desired number of ranks and the desired execution time for the new log (in seconds). In the following example, the lammps log is stretched on 12 ranks (two additional ranks to the original log) and running for one hour (almost double to the original log).

```
$ python extract_patterns_json.py log/lammps/all.trace.json 12 3600
```

The log can also be trimmed by asking for a smaller number of ranks or a smaller execution time. Other options include:

```
$ python extract_patterns_json.py -h
usage: extract_patterns_json.py [-h] [-v] [-i] [-o OUTPUT] [-d DEGREE] [-r RANKVAR] [-s] infile req_ranks req_exec

positional arguments:
  infile                Input TAU json file
  req_ranks             Number of requested ranks
  req_exec              Requested execution time in seconds

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Print debug information
  -i, --interpolate     Repeat only log patterns that can be interpolated
  -o OUTPUT, --output OUTPUT
                        Output file to store the new JSON log
  -d DEGREE, --degree DEGREE
                        Interpolation polynomial degree. Default: linear
  -r RANKVAR, --rankvar RANKVAR
                        Variability among rank duplication. Adds a random noise with a random distribution with a center of 0 and length of value (in seconds).
                        Default: 0 (no variability)
  -s, --stats           Only show stats about the TAU log, do not create a new one. The requested time and ranks will be ignored
```

When increasing the execution time, the code interpolates on the current data and predicts what the I/O pattern will be for the requested execution time. If a certain pattern only occurs once, it will be repeated with a frequency equal to the end of the execution minus it’s timestamp (e.g. the pattern consisting of two reads followed by a write only occurs once at minute 10 in a 20 minute execution, in a new log for a 30 minute execution, this pattern will occur once more at minute 20). If we want to skip those patterns and not repeate them again, the interpolation parameter can be set. The degree parameter changes the interpolation degree for the polynomial fit for this step. 

When increasing the number of ranks, the code clusters the behaviors of existing ranks and multiplies them by copying their execution to the additional ranks. If we want to add variability to the additional ranks, the rankvar parameter can be used. The variability is introduced by adding noise with a uniform distribution between -x and x, where x is the value provided as the parameter (in seconds).

Example running the code using all the parameters:

```
$ python extract_patterns_json.py log/lammps/all.trace.json 12 3600 -o out.json -d 2 -r 10 -i
```

In this case, the code will create a log file called out.json from the lammps trace by extending it to 12 ranks and one hour execution time. It will use a polynomial of degree 2 to interpolate the patterns in the lammps log, it will not repeat patterns that occur only once and it will add variability in the two additional ranks by adding noise following an uniform distribution with center 0 and edges to -10 and 10 seconds.

<img width="667" alt="Screen Shot 2022-07-20 at 4 35 59 PM" src="https://user-images.githubusercontent.com/16229479/180076779-3ca7b984-8cee-4c26-8150-45352088ff2b.png">

**3. Combine multiple applications to create new patterns across the entire execution**

**4. Run the benchmark**

