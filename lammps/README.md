# LAMMPS

## Build LAMMPS on Summit

The instructions assume ADIOS2 is compiled and build on Summit.
Build LAMMPS with cuda and adios. 

```
git clone https://github.com/lammps/lammps.git
mkdir build
cd build

module load cuda
module load gcc

# For laptop I only used cmake ../lammps/cmake
cmake -D PKG_GPU=yes -D GPU_API=cuda -D GPU_ARCH=sm_70 -D PKG_USER-ADIOS=yes -DADIOS2_DIR=/ccs/home/againaru/adios/install/lib64/cmake/adios2 -D PKG_MANYBODY=yes -D PKG_KSPACE=yes -D PKG_MOLECULE=yes -D PKG_OPT=yes -DPKG_RIGID=yes ../lammps/cmake

cmake --build . 
```

## Running LAMMPS on Summit

LAMMPS will be run from `/gpfs/alpine/csc143/proj-shared/againaru/lammps`.

For summit runs the `in.lj.simdata` is used as the input file and `adios2_config.xml` as the ADIOS-2 configuration file.
The submission script can be found in the `batch_submission.sh` file and follows the typical submission script described in the root README, with the following modules and execution command:

```
module load cuda
module load gcc

jsrun -n1 /ccs/home/againaru/lammps/build/lmp -in ./in.lj.simdata
```

Example output file and darshan logs are presented in the `lammps.o` and `lamps.darshan` files respectively. 

## Small scale experiments on laptop

Using input files from the examples folder inside lammps. Experiments were done on the following applications:

**ASPHERE** models aspherical particles with or without solvent.

**ELASTIC** computes elastic constants at zero temperature, using an Si example.
And it's variant, **ELASTIC_T** computes elastic constants at finite temperature.

**HEAT** implements heat exchange algorithms (e.g. used for establishing a thermal gradient).
