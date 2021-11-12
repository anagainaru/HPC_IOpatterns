#!/bin/bash

# Copyright 2019-2020 Maxence Thevenet, Axel Huebl
#
# This file is part of WarpX.
#
# License: BSD-3-Clause-LBNL
#
# Refs.:
#   https://jsrunvisualizer.olcf.ornl.gov/?s4f0o11n6c7g1r11d1b1l0=
#   https://docs.olcf.ornl.gov/systems/summit_user_guide.html#cuda-aware-mpi

#BSUB -P CSC143
#BSUB -W 00:10
#BSUB -nnodes 2
#BSUB -alloc_flags smt4
#BSUB -J WarpX
#BSUB -o WarpXo.%J
#BSUB -e WarpXo.%J

module load gcc
module load cuda

export DARSHAN_DISABLE_SHARED_REDUCTION=1
export DXT_ENABLE_IO_TRACE=4

export OMP_NUM_THREADS=1
jsrun -r 6 -a 1 -g 1 -c 7 -l GPU-CPU -d packed -b rs --smpiargs="-gpu" /gpfs/alpine/csc143/proj-shared/againaru/warpx/warpx/build/bin/warpx.3d.MPI.CUDA.DP.OPMD /gpfs/alpine/csc143/proj-shared/againaru/warpx/warpx/Examples/Physics_applications/uniform_plasma/inputs_3d > output.txt
