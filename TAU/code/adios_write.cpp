#include <adios2.h>
#include <mpi.h>
#include <iostream>
#include <fstream>
using namespace std;

int main (int argc, char *argv[]) {
   MPI_Init(&argc, &argv);

    const std::string myString("Hello Variable String");
	adios2::ADIOS adios(MPI_COMM_WORLD);
	adios2::IO bpIO = adios.DeclareIO("WriteBP");
    adios2::Variable<std::string> bpString =
            bpIO.DefineVariable<std::string>("bpString");
	adios2::Engine bpFileWriter = bpIO.Open("input_file", adios2::Mode::Write);
	bpFileWriter.Put(bpString, myString);
	bpFileWriter.Close();

   MPI_Finalize();   
   return(0);
}
