# NWChem

**Build NWChem**

NWChem requires ADIOS2 to run. The follwing steps assume ADIOS-2 is builed and compiled with Fortran and python enabled (as described by the steps in the root README).

Download NWChem following the following steps:

```
module load gcc
module load cmake
module load python

source_dir=`pwd`
git clone https://github.com/pnorbert/nwchem.git
cd nwchem
git checkout adios2-global
export NWCHEM_HOME="${source_dir}/nwchem"
cd ..
```
The downloaded code for the testing in this repository can be found at `/gpfs/alpine/csc143/proj-shared/againaru/nwchem`
To build the code create the `runconf.nwchem` file with the bellow content (file also available in this repo) and follow the steps:

```
$ cat runconf.nwchem
export NWCHEM_TOP=/gpfs/alpine/csc143/proj-shared/againaru/nwchem/code_with_adios
export NWCHEM_TARGET=LINUX64
export NWCHEM_MODULES=md
export USE_INTERNALBLAS=y
export USE_MPI=y
export USE_ADIOS2=y
export ADIOS2_DIR=/ccs/home/againaru/adios/adios2-install

make nwchem_config

echo "Now run make..."

$ cd src
$ source ../runconf.nwchem
$ make -j
```

The binaries will be placed in `${NWCHEM_TOP}/bin/LINUX64`

The script `build_nwchem.sh` builds both ADIOS-2 and NWChem in the current directory.

**Paths for Summit:**

Source code compiled and build for Summit:
`/gpfs/alpine/csc143/proj-shared/againaru/nwchem`

Source code compiled and built for Rhea:
`/ccs/proj/csc143/nwchem/source/nwchem.rhea`

The code with ADIOS outputs the trajectory in a global array.

Input file and batch_submission scripts are in:
`/gpfs/alpine/csc143/proj-shared/againaru/nwchem/summit_submit`


**Input files**

* `copro.nw` is the configuration file and the parameter to run nwchem
* `copro.top` is the topology file
* `copro_md.rst` is the restart file
* `adios2.xml` is the configuration file for ADIOS

**Batch script**

`nwchem.sh` is a sample job script that couples nwchem (generate the trajectory) and sorting (sort the generated trajectory)

```
bsub nwchem.sh
```

**Output**

The script creates an output file `nwchem-sort.o{$JOBID}` with both stdout and stderr. Example output file can be found in `nwchem-sort.o` and corresponding Darshan file in `nwchem.darshan`.

