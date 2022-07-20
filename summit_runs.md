## I/O benchmark on Summit
### Running the benchmark

_Prerequisites_: A collection of TAU logs that capture the I/O of applications that will be used to create the benchmark

_Output_: An executable that can be submitted on Summit to simulate the execution of the input applications 

_Steps_: 
1. Combine multiple logs to create new patterns within one application
2. Modify existing logs to fit the simulation parameters (execution time, number of cores, etc.)
3. Combine multiple applications to create new patterns across the entire execution
4. Run the benchmark

NOTE. All logs can be visualized with the chrome tracer at: [chrome://tracing/](chrome://tracing/)

**1. Combine multiple logs to create new patterns within one application**

Example logs are provided in the log folder, with one folder for one application.
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

**3. Combine multiple applications to create new patterns across the entire execution**

**4. Run the benchmark**

