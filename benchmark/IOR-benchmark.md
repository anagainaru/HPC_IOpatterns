# Running the modified IOR benchmark

Code from: (https://github.com/xiexbing/hdf5-work/tree/master/ior_mod)[https://github.com/xiexbing/hdf5-work/tree/master/ior_mod]

The modified version of the code is stored in the `ior_mod` folder.

## Build the codes

Both codes follow the same pattern for build.

```
./configure --prefix=/gpfs/alpine/csc143/proj-shared/againaru/olcf/IOR-bing/build/ior_mod/
make
make install
```

The IOR modified version lacks a few files needed to build that can be copied from the IOR folder (specifically `config/config.*` and `src/config.h*`)
Each code is currently build on Summit in the folder: `./configure --prefix=/gpfs/alpine/csc143/proj-shared/againaru/olcf/IOR-bing/build`

## Running on Summit

Files for submitting on Summit can be found in the `summit_experiment/` folder.
The `summit_template.sh` file needs to be update with the correct paths to the IOR executables.

```
d_ior=/gpfs/alpine/csc143/proj-shared/againaru/olcf/IOR-bing/build/ior/src/ior
m_ior=/gpfs/alpine/csc143/proj-shared/againaru/olcf/IOR-bing/build/ior_mod/src/ior
```
