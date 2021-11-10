cmake_minimum_required(VERSION 3.12)
project(TAUsimple CXX C)

find_package(MPI REQUIRED)
find_package(adios2 REQUIRED)

add_executable(simple.write simple_write.cpp)
target_link_libraries(simple.write MPI::MPI_CXX)

add_executable(simple.read simple_read.cpp)
target_link_libraries(simple.read MPI::MPI_CXX)

add_executable(adios.write adios_write.cpp)
target_link_libraries(adios.write adios2::adios2 MPI::MPI_CXX)

add_executable(adios.read adios_read.cpp)
target_link_libraries(adios.read adios2::adios2 MPI::MPI_CXX)
