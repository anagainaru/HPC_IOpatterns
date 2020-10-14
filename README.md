## Analyzing the I/O patterns for the CORAL-2 benchmark

### CORAL-2 benchmark

The repo contains one folder for each benchmark ([CORAL-2 suite](https://asc.llnl.gov/coral-2-benchmarks)) we analyze. Details on how to install/run each benchmark and performance details can be found in each folder.

We use Darshan ([Darshan website](https://www.mcs.anl.gov/research/projects/darshan/)) in order to extract I/O performance counters

### 1. Installing and running with Darshan

```
# download darshan, installing darshan-runtime
./configure --with-log-path=/home/anagainaru/work/darshan/logs --with-jobid-env=NONE CC=mpicc --prefix=/home/anagainaru/work/darshan/darshan-install
make -j
make install

#install darshan util
./configure --prefix=/home/anagainaru/work/darshan/darshan-install/
make -j
make install

export LD_PRELOAD=/home/anagainaru/work/darshan/darshan-install/lib/libdarshan.so 
export DARSHAN_LOGPATH=/home/anagainaru/work/darshan/logs

# prepare the log directory hieararchy
../darshan-install/bin/darshan-mk-log-dirs.pl 
```

Once all these steps are done, static compilation using mpicc will automatically link darshan to the code.
Using mpirun will automatically create a log in the path given by `$DARSHAN_LOGPATH` 
Logs will be named: `user_executable_id_date.darshan`

```
ls /home/anagainaru/work/darshan/logs/2020/10/14
anagaina_hello_id29653_10-14-51933-1508791425251891109_1602699934.darshan
```

### 2. Parsing logs generated by Darshan

To create a PDF report of the profile:
```
./darshan-install/bin/darshan-job-summary.pl <trace_file>.darshan
```

To generate a ascii file with the information in the darshan trace file:
```
 ./darshan-install/bin/darshan-parser <trace_file>.darshan
 
 # list of files opened and the amount of time spent performing IO
 darshan-parser --file-list <trace_file>.darshan
```
