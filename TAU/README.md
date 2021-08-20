# Gathering logs with TAU

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



