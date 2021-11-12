cmake_minimum_required(VERSION 3.0)

project (simple)

find_package(MPI REQUIRED) 
include_directories(SYSTEM ${MPI_INCLUDE_PATH})

SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fopenmp")

add_executable(simple simple-io.c)
target_link_libraries(simple ${MPI_C_LIBRARIES})
