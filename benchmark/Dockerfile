FROM ubuntu:latest

RUN mkdir -p /install/cheetah

RUN apt-get update && apt-get install -y \
    python3 \
    pip \
    cmake \
    vim \
    git \
    mpich

RUN alias python=python3

RUN pip install numpy
RUN pip install cheetah3 --prefix=/install/cheetah

RUN cd /install && \
    git clone https://github.com/ornladios/ADIOS2.git && \
    cd ADIOS2 && \
    mkdir build && cd build && \
    cmake -DCMAKE_INSTALL_PREFIX=/install/ADIOS2/install -DADIOS2_USE_PYTHON=ON .. && \
    make -j4 && make -j4 install

ENV ADIOS2_DIR=/install/ADIOS2/install
ENV PYTHONPATH=${ADIOS2_DIR}/lib/python3/dist-packages:/install/cheetah/local/lib/python3.10/dist-packages:$PYTHONPATH
ENV LD_LIBRARY_PATH=${ADIOS2_DIR}/lib:${LD_LIBRARY_PATH}
