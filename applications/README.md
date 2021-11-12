# Tools to gather I/O logs

[TAU](#tau) <br/>
[Darshan](#darshan)

# TAU

Info on running TAU on Summit [github link](https://github.com/UO-OACISS/tau2/wiki/Using-TAU-to-Profile-and-or-Trace-ADIOS)
and [olcf webpage](https://docs.olcf.ornl.gov/software/profiling/TAU.html).

## Installing TAU

They have fixed some issues with multi-threaded I/O libraries and the version Summit is using is old (2.29.1)

In order to install a newer version that tracks timestamp information:

```
wget http://tau.uoregon.edu/tau2.tgz
tar xzvf tau2.tgz
```
or
```
git clone https://github.com/UO-OACISS/tau2.git tau2
```
and configure it with:
```
./configure -mpi -c++=mpicxx -cc=mpicc -fortran=mpif90 -bfd=download -iowrapper -pthread 
make install 
export PATH=/gpfs/alpine/csc143/proj-shared/againaru/tau2/ibm64linux/bin:$PATH
```

## Using TAU on Summit

In order to get summary information.
```
module load tau
tau_exec -T mpi {options} app_exec app_param
```
The options include:
- `optTrackIO`	Wrap POSIX I/O call and calculate vol/bw of I/O operations
- io (track io)

Once the execution is done, the files can be analyzed with `pprof`.
```
$ pprof profile.0.0.0
Reading Profile files in profile.*

NODE 0;CONTEXT 0;THREAD 0:
---------------------------------------------------------------------------------------
%Time    Exclusive    Inclusive       #Call      #Subrs  Inclusive Name
              msec   total msec                          usec/call
---------------------------------------------------------------------------------------
100.0        0.038     1:10.733           1           1   70733442 .TAU application
100.0            9     1:10.733           1        4654   70733404 int main(int, char **)
 97.1           15     1:08.668        4501       27006      15256 void perform_timestep(double *, double *, double *, double *, double)
 97.1        1,167     1:08.653       27006       54012       2542 void semi_discrete_step(double *, double *, double *, double, int, double *, double *)
 48.4       34,240       34,240       13503           0       2536 void compute_tendencies_z(double *, double *, double *)
 46.9       33,199       33,199       13503           0       2459 void compute_tendencies_x(double *, double *, double *)
  2.5          224        1,752         151       33361      11608 void output(double *, double)
  1.7        1,211        1,211         604         604       2006 MPI_File_write_at_all()
  0.4           36          250           1      100003     250708 void init(int *, char ***)
...


USER EVENTS Profile :NODE 0, CONTEXT 0, THREAD 0
---------------------------------------------------------------------------------------
NumSamples   MaxValue   MinValue  MeanValue  Std. Dev.  Event Name
---------------------------------------------------------------------------------------
      1058    1.6E+05          4  9.134E+04  7.919E+04  MPI-IO Bytes Written
       454        284          4      5.947       13.2  MPI-IO Bytes Written : int main(int, char **) => void output(double *, double) => MPI_File_write_at()
       604    1.6E+05    1.6E+05    1.6E+05          0  MPI-IO Bytes Written : int main(int, char **) => void output(double *, double) => MPI_File_write_at_all()
      1058       9412     0.1818       3311       3816  MPI-IO Write Bandwidth (MB/s)
       454      1.856     0.1818     0.5083     0.1904  MPI-IO Write Bandwidth (MB/s) : int main(int, char **) => void output(double *, double) => MPI_File_write_at()
       604       9412      2.034       5799       3329  MPI-IO Write Bandwidth (MB/s) : int main(int, char **) => void output(double *, double) => MPI_File_write_at_all()
       755          8          8          8          0  Message size for all-reduce
       302  2.621E+05          4  1.302E+05  1.311E+05  Message size for broadcast
---------------------------------------------------------------------------------------
```

Files can be packed (and later unpacked) in ppk format.
```bash
paraprof --pack name.ppk
paraprof --dump name.ppk
pprof > tau_adios2_variable_shapes_hl.out
```

## Tracing with TAU

Profiles contain summary information, traces provide temporal information. 

Running an application and gathering tracing for it requires setting the `TAU_TRACE` variable. The information can then be dumped with `tau_convert` to show the text contents. 
```bash
export TAU_TRACE=1
tau_convert -dumpname <.trc file> <edf file> 
```

Example output
```
#=NO= ==TIME [us]= =NODE= =THRD= ==PARAMETER= =======================EVENT==
 1502 1628710611659481    160      0            1 "IO::Open "
 1554 1628710611948365    160      0            0 "Message size received in wait : IO::Open => BP4Writer::Open => MPI_Wait()  "
 1575 1628710611949522    160      0           -1 "BP4Writer::Open "
 1577 1628710611949573    160      0            1 "BP4Writer::BeginStep "
 1578 1628710611949578    160      0           -1 "BP4Writer::BeginStep "
 1579 1628710611949612    160      0            1 "IO::InquireVariable "
 1589 1628710612092069    160      0            1 "BP4Writer::EndStep "
 1590 1628710612092076    160      0            1 "BP4Writer::PerformPuts "
 1628 1628710612092280    160      0            1 "BP4Writer::Flush "
 1629 1628710612092289    160      0            1 "BP4Writer::AggregateWriteData "
 259941 1628710612524381    160      0            1 "BP4Writer::Close "
 1628 1628710612092280    160      0            1 "BP4Writer::Flush "
 2105 1628710612110480    160      0            1 "BP4Writer::WriteCollectiveMetadataFile "
260200 1628710612527160    160      0            1 "BP4Writer::WriteProfilingJSONFile "
259956 1628710612524414    160      0            0 "Message size received in wait : BP4Writer::Close => BP4Writer::AggregateWriteData => MPI_Wait()  "
 1649 1628710612092396    160      0            0 "Message size received in wait : BP4Writer::EndStep => BP4Writer::Flush => BP4Writer::AggregateWriteData => MPI_Wait()  "
  983 1628710611655952    160      0            1 "IO::DefineAttribute "
 1001 1628710611656147    160      0            1 "IO::DefineVariable "
 1579 1628710611949612    160      0            1 "IO::InquireVariable "
 1596 1628710612092199    160      0            1 "IO::InquireAttribute "
 1592 1628710612092105    160      0           -1 "IO::other "

260402 1628710612607793    160      0            0 "TAU_TRACK_IO_PARAMS | off"
```

### Visual inspection

Alternatively, the trace can be viewd with Vampire by activating tracing and declaring the data format to OTF2. OTF2 format is supported only by MPI and OpenSHMEM applications.

```
export TAU_TRACE=1
export TAU_TRACE_FORMAT=OTF2
vampir traces.otf2 &
```



# Darshan

This folder contains one folder for each application we analyze (and the `simple_example` folder for a simple example that uses both MPI-IO and Posix in addition to standard output).
Details on how to install/run each benchmark and performance details can be found in each folder.

## List of Applications

* **LAMMPS**: Molecular Dynamics Simulator ([Link](https://lammps.sandia.gov/))
* **NWChem**: Open Source High-Performance Computational Chemistry ([Link](https://nwchemgit.github.io/))
* **WarpX**: Advanced Electromagnetic Particle-In-Cell ([Link](https://warpx.readthedocs.io/en/latest/))

## Steps to analyze the IO patterns
We use Darshan ([Darshan website](https://www.mcs.anl.gov/research/projects/darshan/)) for extracting the I/O patterns.

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

On Summit Darshan is installed by default and logs are gathered for every MPI application in the folder:
`/gpfs/alpine/darshan/summit/year/month/day/your-job-ID`

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

On Summit Darhsan util is available to be loaded as a module.

```
$ module load darshan-util
$ darshan-job-summary.pl <trace_file>.darshan
```

## Submission on Summit

Example submission script:

```
#!/bin/bash -l
#BSUB -P CSC143
#BSUB -W 00:30
#BSUB -nnodes {$nnodes}
#BSUB -J name
#BSUB -o name.o%J
#BSUB -e name.o%J

# Allow Darshan logs to be collected
export DARSHAN_DISABLE_SHARED_REDUCTION=1
export DXT_ENABLE_IO_TRACE=4

# import all required modules

jsrun -n {$nnodes} ./executable parameters
```

To submit `bsub script.sh` which will generate a `name.o{$JobID}` file with the stdout and stderr and a Darshan log file in `/gpfs/alpine/darshan/summit/year/month/day/your-job-ID`

### Modules version

Versions used when testing all the script.

```
cuda/10.1.243 (D)
cmake/3.18.2 (D)
gcc/6.4.0 (D)
python/3.6.6-anaconda3-5.3.0 
```
