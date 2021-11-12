# WarpX

**Files in this folder**

* `warpx.profile` script used to load all modules and environmental variables needed by warpx
* `batch_summit.sh` script file to submit warpx on summit
* `output.txt` example standard output generated when running warpx (example for the uniform_plasma 3d input file)
* `darshan` folder with darshan logs and statistics for all the input files described below

Root folder for warpx where the experiments have been done:
`/gpfs/alpine/csc143/proj-shared/againaru/warpx`

Darshan files are generated in:
`/gpfs/alpine/darshan/summit/year/month/day/{username}_{exec}_id{proc_id}*`

**Build Warpx**

Instructions on building WarpX on Summit can be found [here](https://warpx.readthedocs.io/en/latest/building/summit.html)

Create a new folder where all the different applications will be stored

```
git clone https://github.com/ECP-WarpX/WarpX.git warpx
git clone --branch development https://github.com/ECP-WarpX/picsar.git
git clone --branch development https://github.com/AMReX-Codes/amrex.git
```

Create a warpx.profile file in the root folder that loads all the reqiured modules (similar to the one in the repo).

```
source {$HOME_WARPX}/warpx.profile
cd {$HOME_WARPX}/src/warpx

mkdir -p build
cd build
cmake .. -DWarpX_OPENPMD=ON -DWarpX_DIMS=3 -DWarpX_COMPUTE=CUDA -DCMAKE_CUDA_ARCHITECTURES=70 -DCUDA_ARCH=7.0
make -j 10
``` 

**Submitting Warpx on Summit**

Example script files can be found [here](https://warpx.readthedocs.io/en/latest/running_cpp/platforms.html#running-cpp-summit).
All the necessary modules need to be loaded. A working example can be found in this repo in the `batch_summit.sh` file.

```
bsub batch_summit.sh
```

The script creates a `warpx.o` out put file with stderr and information about the scheduled job, `output.txt` with stdout and a folder `diags` with the simulation output.

**Input files**

Input files can be found in the `{$WARPX_ROOT}/warpx/Examples/` folder. Darshan logs were collected for the following input files:
* `Examples/Tests/collision/inputs_3d`
* `Examples/Physics_applications/uniform_plasma/inputs_3d`
* `Examples/Physics_applications/plasma_acceleration/inputs_3d_boost`
* `Examples/Physics_applications/laser_acceleration/inputs_3d`
