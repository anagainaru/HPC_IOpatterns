#!/bin/bash -l
#BSUB -P CSC143
#BSUB -W 00:30
#BSUB -nnodes 15
#BSUB -J lammps
#BSUB -o lammps.o%J
#BSUB -e lammps.o%J

export DARSHAN_DISABLE_SHARED_REDUCTION=1
export DXT_ENABLE_IO_TRACE=4

module load cuda
module load gcc

jsrun -n 224 /ccs/home/againaru/lammps/build/lmp -in ./in.lj.simdata
