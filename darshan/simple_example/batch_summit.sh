#!/bin/bash
#BSUB -P CSC143
#BSUB -W 00:10
#BSUB -nnodes 1
#BSUB -J simple
#BSUB -o simple.%J
#BSUB -e simple.%J

module load gcc
module load openmpi
module load darshan-runtime

export DARSHAN_LOGPATH=/gpfs/alpine/csc143/proj-shared/againaru/logs

mpirun -n 10 ./build/simple /ccs/home/againaru/darshan/simple_example/temp
