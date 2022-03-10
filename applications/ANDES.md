# Running with TAU on ANDES

## Install TAU-2

```
wget http://tau.uoregon.edu/tau2.tgz
tar xzvf tau2.tgz
```
(or `git clone https://github.com/UO-OACISS/tau2.git tau2`)

```
./configure -mpi -c++=mpicxx -cc=mpicc -fortran=mpif90 -bfd=download -iowrapper -pthread 
make install 
export PATH=/gpfs/alpine/csc143/proj-shared/againaru/tau2/ibm64linux/bin:$PATH
```

**Later EDIT** New version of Github latest branch TAU is installed in `/gpfs/alpine/csc143/proj-shared/againaru/tau_github/ibm64linux/bin` 

TAU in installed in the folder `/ccs/home/againaru/util/tau2`
To use it you need to include the path to the tau_exec executable in the PATH variable.
```
export PATH=/ccs/home/againaru/util/tau2/x86_64/bin:$PATH
```

## Run on ANDES


Currently we can use TAU only for MPI applications (if we want the skel functionality)
A script example (andes_submit.sh):

```
#!/bin/bash
#SBATCH -A CSC143
#SBATCH -J tau_testing
#SBATCH -N 1
#SBATCH -t 0:00:10

export PATH=/ccs/home/againaru/util/tau2/x86_64/bin:$PATH

srun -n 1 tau_exec -T mpi -io -skel ./simple.write
```

Andes is using slurm so use the following commands to submit the job and check for it’s status: 

```
sbatch andes_submit.sh
squeue --user=againaru
```

The output is a slurm file and a directory called skel containing the TAU logs.
To gather information about the run:

```
sacct --format=jobid,jobname,partition,CPUTime,Elapsed,ExitCode,NNodes | grep [jobid]
```

We are interested in gathering the execution time and the log for each application
