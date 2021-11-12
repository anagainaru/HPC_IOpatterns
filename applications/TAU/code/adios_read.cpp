#include <adios2.h>
#include <mpi.h>
#include <iostream>
#include <fstream>
using namespace std;

int main (int argc, char *argv[]) {
   MPI_Init(&argc, &argv);

	adios2::ADIOS adios(MPI_COMM_WORLD);
	adios2::IO bpIO = adios.DeclareIO("WriteBP");
	adios2::Engine bpReader = bpIO.Open("input_file", adios2::Mode::Read);
	std::string myString;
	adios2::Variable<std::string> bpString = 
			 bpIO.InquireVariable<std::string>("bpString");
	bpReader.Get<std::string>(bpString, myString);
	bpReader.Close();

    std::cout << myString << std::endl;
   MPI_Finalize();   
   return(0);
}
