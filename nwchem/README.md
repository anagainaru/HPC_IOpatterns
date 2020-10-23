# NWChem

**ADIOS2**

ADIOS2 needs to be build with Fortran enabled

```
cmake -DADIOS2_USE_Fortran=ON -DCMAKE_Fortran_COMPILER=gfortran ../ADIOS2
make -j
cmake -D CMAKE_INSTALL_PREFIX=/ccs/home/againaru/adios/adios2-install ../ADIOS2/
make -j install
```

**Build NWChem**

Download NWChem. Create the `runconf.nwchem` script file in the `NWCHEM_TOP` directory
and follow the following steps:

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

**Paths for Summit:**

Source code compiled and build for Summit:
`/gpfs/alpine/csc143/proj-shared/againaru/nwchem/code_with_adios`

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

`nwchem_sorting.sh` is a sample job script that couples nwchem (generate the trajectory) and sorting (sort the generated trajectory)

```
bsub nwchem_sorting.sh
```

**Output**

The script creates an output file `nwchem-sort.o{$JOBID}` and generated Darshan files with DXT enabled.

