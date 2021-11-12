<img src="logo.png" align="right" alt="Logo" width="350"/>

# Benchmark for large-scale I/O patterns

Code and scripts are stored on Summit in `/gpfs/alpine/csc143/proj-shared/againaru/olcf`.

[More details on TAU logs](#tau) <br/>
[More details on Darshan logs](#darshan) <br/>
[Aggregated I/O patterns](#aggregated-patterns) <br/>
[Time series I/O patterns](#time-series-patterns) <br/>
[Benchmark](#benchmark)

## TAU

Source code can be downloaded from: [https://github.com/UO-OACISS/tau2.git](https://github.com/UO-OACISS/tau2.git)

```
tau_exec -T mpi -io -skel ./executable parameters
```

Logs can be visualized using [chrome://tracing/](chrome://tracing/)  

Example log
```
[
{"ts": 1630009505960310, "dur": 179, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "fopen64", "args": {"path": "input_file.txt", "mode": "rb"}, "return": "0x1c5f9b50"},
{"ts": 1630435888978714, "dur": 280, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "open", "args": {"pathname": "input_file/md.0", "flags": 577, "mode": 438}, "return": 22},
]
```

More details on building and running TAU on Summit/Andes: [here](./applications/README.md)

## Darshan

We use Darshan ([Darshan website](https://www.mcs.anl.gov/research/projects/darshan/)) for extracting the I/O patterns.

On Summit Darshan is installed by default and logs are gathered for every MPI application in the folder:
`/gpfs/alpine/darshan/summit/year/month/day/your-job-ID`

For Andes the location of the logs is `/gpfs/alpine/darshan/andes`

To generate the ascii file with the information in the darshan trace file:
```
 darshan-parser --file-list <trace_file>.darshan > <file>.log
 darshan-parser <trace_file>.darshan >> <file>.log
```

For DXT logs, the darshan-dxt environmental variables need to be set
```
export DARSHAN_DISABLE_SHARED_REDUCTION=1
export DXT_ENABLE_IO_TRACE=4
```
after which the ascii file can be generated using
```
 darshan-dxt-parser <trace_file>.darshan > <file>.dxt.log
```

The `darshan-dxt-to-json.py` script can be used to convert the dxt output into JSON format that can be visualized with `chrome://tracing` 
```
$ python darshan-dxt-to-json.py lammps/darshan/lammps.dxt.log
[
{"ts": 41200, "cat": "X_POSIX", "dur": 1, "tid": 0, "ph": "X", "name": "read", "pid": 0, "args": {"Segment": "0", "Offset": "0", "mnt_pt:": "/gpfs/alpine,", "fs_type:": "gpfs", "rank:": "0,", "hostname:": "h50n18", "file_name:": "/gpfs/alpine/csc143/proj-shared/againaru/lammps/adios2_config.xml", "Length": "1436", "file_id:": "17123874527013665068,"}},
{"ts": 41200, "cat": "X_POSIX", "dur": 1, "tid": 0, "ph": "X", "name": "read", "pid": 0, "args": {"Segment": "1", "Offset": "1436", "Length": "0"}},
{"ts": 132200, "cat": "X_POSIX", "dur": 1, "tid": 0, "ph": "X", "name": "write", "pid": 0, "args": {"Segment": "0", "Offset": "0", "mnt_pt:": "/gpfs/alpine,", "fs_type:": "gpfs", "rank:": "0,", "hostname:": "h50n18", "file_name:": "/gpfs/alpine/csc143/proj-shared/againaru/lammps/lj_adios_output.bp/data.0", "Length": "3585374", "file_id:": "7146724260063322621,"}},
{"ts": 2468000, "cat": "X_POSIX", "dur": 1, "tid": 0, "ph": "X", "name": "write", "pid": 0, "args": {"Segment": "1", "Offset": "3585374", "Length": "3584815"}},
{"ts": 4828600, "cat": "X_POSIX", "dur": 1, "tid": 0, "ph": "X", "name": "write", "pid": 0, "args": {"Segment": "2", "Offset": "7170189", "Length": "3584815"}}
]
```

More details on building and running Darshan on Summit/Andes: [here](./applications/README.md)

## Aggregated patterns

## Time Series patterns

## Benchmark

