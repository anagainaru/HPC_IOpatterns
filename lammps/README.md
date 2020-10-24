# LAMMPS

## Build LAMMPS on Summit

The instructions assume ADIOS2 is compiled and build on Summit.

```
git clone https://github.com/lammps/lammps.git
```

Build LAMMPS with cuda and adios. 

```
module load cuda

# For laptop I only used cmake ../lammps/cmake
cmake -D PKG_GPU=yes -D GPU_API=cuda -D GPU_ARCH=sm_70 -D PKG_USER-ADIOS=yes -DADIOS2_DIR=/ccs/home/lwan86/adios2-master-summit/install-dir/lib64/cmake/adios2 -D PKG_MANYBODY=yes -D PKG_KSPACE=yes -D PKG_MOLECULE=yes -D PKG_OPT=yes -DPKG_RIGID=yes ../lammps/cmake

cmake --build . 
```

## Running LAMMPS on Summit



## Small scale experiments on laptop

Using input files from the examples folder inside lammps. Experiments were done on the following applications:

**ASPHERE** models aspherical particles with or without solvent.

**ELASTIC** computes elastic constants at zero temperature, using an Si example.
And it's variant, **ELASTIC_T** computes elastic constants at finite temperature.

**HEAT** implements heat exchange algorithms (e.g. used for establishing a thermal gradient).

