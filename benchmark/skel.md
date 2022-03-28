# Skel-IO benchmark

Starting from the code in [https://github.com/isosc/skel-io](https://github.com/isosc/skel-io)

**Build the benchmark**

Instructions for ANDES, prerequisites include adios and cheetah3.

```
pip install cheetah3 --prefix=/autofs/nccs-svm1_home1/againaru/.local/lib/python3.6/site-packages
module load cmake
export ADIOS2_DIR=/ccs/home/againaru/adios/ADIOS2/install_andes
export PYTHONPATH=${ADIOS2_DIR}/lib64/python3.6/site-packages:/autofs/nccs-svm1_home1/againaru/.local/lib/python3.6/site-packages
export LD_LIBRARY_PATH=${ADIOS2_DIR}/lib64/:${LD_LIBRARY_PATH}
```

The Makefile in the `tests/lammps/small` folder can be used test the benchmark on a given set of applications.
```
make clean
make create
make build
make run
```

The `trace` folder needs to exist next to the Makefile containing the skel config file and the trace logs (each application needs an individual folder called `application_{i}`).
In each application folder the TAU logs need to be stord.

Example:
```
$ ls trace/*
trace/skel-io.json

trace/application1:
rank00000.trace  rank00001.trace  rank00002.trace  rank00003.trace

trace/application2:
rank00000.trace  rank00001.trace  rank00002.trace
```

**Modifications to the code**
