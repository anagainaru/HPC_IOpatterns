#!/bin/bash -l
#BSUB -P CSC143
#BSUB -W 00:30
#BSUB -nnodes 15
#BSUB -J nwchem
#BSUB -o nwchem.o%J
#BSUB -e nwchem.o%J

N_NWCHEM=224
N=224
NNODES= 15

HOME=/gpfs/alpine/csc143/proj-shared/againaru/nwchem/summit_submit
NWCHEM=/gpfs/alpine/csc143/proj-shared/againaru/nwchem

module load gcc
module load cmake
module load python

export DARSHAN_DISABLE_SHARED_REDUCTION=1
export DXT_ENABLE_IO_TRACE=4

rm -rf copro_md_trj_dump.bp
rm -rf copro_md_trj.bp

CONFIG=copro-${N_NWCHEM}.txt

(( N = N_NWCHEM + N_SORTER ))
(( NWCHEM_PPN = N_NWCHEM / NNODES ))

echo "Nodes         = ${NNODES}"
echo "NWChem nproc  = ${N_NWCHEM}"
echo "NWChem ppn    = ${NWCHEM_PPN}"

#export SstVerbose=1
jsrun -n ${N} $NWCHEM/bin/LINUX64/nwchem copro.nw

