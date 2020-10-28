# please set your project account
export proj=CSC143
export HOME_WARPX=`pwd`

# required dependencies
module load cmake
module load gcc/6.4.0
module load cuda

# optional: faster re-builds
module load ccache

# optional: for PSATD support
module load fftw

# optional: for QED support
module load boost/1.66.0

# optional: for openPMD support
module load ums
module load ums-aph114
module load openpmd-api/0.12.0

# optional: for PSATD in RZ geometry support
#   note: needs the ums modules above
module load blaspp
module load lapackpp

# optional: Ascent in situ support
#   note: build WarpX with CMake
export Alpine=/gpfs/alpine/world-shared/csc340/software/ascent/0.5.3-pre/summit/cuda/gnu
export Ascent_DIR=$Alpine/ascent-install
export Conduit_DIR=$Alpine/conduit-install

# optional: for Python bindings or libEnsemble
module load python/3.7.0

# optional: for libEnsemble
module load openblas/0.3.9-omp
module load netlib-lapack/3.8.0
if [ -d "$HOME_WARPX/sw/venvs/warpx-libE" ]
then
  source $HOME_WARPX/sw/venvs/warpx-libE/bin/activate
fi

# optional: just an additional text editor
module load nano

# optional: an alias to request an interactive node for two hours
alias getNode="bsub -P $proj -W 2:00 -nnodes 1 -Is /bin/bash"

# fix system defaults: do not escape $ with a \ on tab completion
shopt -s direxpand

# compiler environment hints
export CC=$(which gcc)
export CXX=$(which g++)
export FC=$(which gfortran)
export CUDACXX=$(which nvcc)
export CUDAHOSTCXX=$(which g++)
