#! /bin/bash

source_dir=`pwd`
module load gcc
module load cmake
module load python
# build adios2
if [ -d "$ADIOS2_HOME" ]
then
    echo "Using existing ADIOS2_HOME build: $ADIOS2_HOME"
else
    git clone https://github.com/ornladios/ADIOS2
    cd ADIOS2
    mkdir -p install
    mkdir -p build
    export ADIOS2_HOME="${source_dir}/ADIOS2/install"
    cd build
    cmake -DADIOS2_USE_Fortran=ON -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -DCMAKE_Fortran_COMPILER=gfortran -DCMAKE_INSTALL_PREFIX=${ADIOS2_HOME} ..
    make -j 16 && make install
    cd ../..
fi
# build nwchem
if [ -d "$NWCHEM_HOME" ]
then
    echo "Using existing NWCHEM_HOME: $NWCHEM_HOME"
else
    git clone https://github.com/pnorbert/nwchem.git
    cd nwchem
    git checkout adios2-global
    export NWCHEM_HOME="${source_dir}/nwchem"
    cd ..
fi
cd nwchem
# generate runconf.nwchem
echo "export NWCHEM_TOP=${NWCHEM_HOME}" > runconf.nwchem
echo "export NWCHEM_TARGET=LINUX64" >> runconf.nwchem
echo "export NWCHEM_MODULES=md" >> runconf.nwchem
echo "export USE_INTERNALBLAS=y" >> runconf.nwchem
echo "export USE_MPI=y" >> runconf.nwchem
echo "export USE_ADIOS2=y" >> runconf.nwchem
echo "export ADIOS2_DIR=${ADIOS2_HOME}" >> runconf.nwchem
echo "" >> runconf.nwchem
echo "make nwchem_config" >> runconf.nwchem
echo "" >> runconf.nwchem
cat runconf.nwchem
cd src
source ../runconf.nwchem
make -j 16

