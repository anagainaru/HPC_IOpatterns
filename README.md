
<img src="logo.png" align="right" alt="Logo" width="350"/>

## Analyzing the I/O patterns for scientific applications

The repo contains one folder for each application we analyze (and the `simple_example` folder for a simple example that uses both MPI-IO and Posix in addition to standard output).
Details on how to install/run each benchmark and performance details can be found in each folder.

The `analysis` folder contains scripts for analyzing the Darshan logs generated by applications.

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

### 3. Install ADIOS2

For applications using ADIOS-2, the library needs to be installed. Instruction for Summit:

```
git clone https://github.com/ornladios/ADIOS2.git
cd ADIOS2/
mkdir build
cd build/

module load cmake
module load gcc
module load python
module load cuda

cmake -DADIOS2_USE_Fortran=ON -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -DCMAKE_Fortran_COMPILER=gfortran ..
make -j
cmake -D CMAKE_INSTALL_PREFIX=/ccs/home/againaru/adios/install ../ADIOS2/
make -j install
```

Libraries used to link ADIOS-2 with applications can be found in `{$INSTALL_DIR}/lib64/cmake/adios2/`

```
[againaru@login5.summit ~]$ ls /ccs/home/againaru/adios/install/lib64/cmake/adios2/
CMakeFindDependencyMacro.cmake  Findpugixml.cmake
FindBZip2.cmake                 adios2-c-targets-release.cmake
FindBlosc.cmake                 adios2-c-targets.cmake
FindCrayDRC.cmake               adios2-config-common.cmake
FindDataSpaces.cmake            adios2-config-version.cmake
FindHDF5.cmake                  adios2-config.cmake
FindIME.cmake                   adios2-cxx11-targets-release.cmake
FindLIBFABRIC.cmake             adios2-cxx11-targets.cmake
FindMGARD.cmake                 adios2-fortran-targets-release.cmake
FindMPI.cmake                   adios2-fortran-targets.cmake
FindPkgConfig.cmake             adios2-targets-release.cmake
FindPython.cmake                adios2-targets.cmake
FindPythonModule.cmake          thirdparty
FindSZ.cmake                    upstream
FindZeroMQ.cmake
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
