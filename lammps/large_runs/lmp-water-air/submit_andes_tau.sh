#!/bin/bash
#SBATCH -A CSC143
#SBATCH -J lammps
#SBATCH -N 20
#SBATCH -t 1:00:00

module unload darshan

export PATH=/ccs/home/againaru/util/tau2/x86_64/bin:$PATH

srun -n 20 tau_exec -T mpi -io -skel /gpfs/alpine/csc143/proj-shared/againaru/lammps/build_andes/lmp -in ./input.lammps
