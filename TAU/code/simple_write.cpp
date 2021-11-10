#include <mpi.h>
#include <iostream>
#include <fstream>
using namespace std;

int main (int argc, char *argv[]) {
   MPI_Init(&argc, &argv);

   ofstream myfile;
   myfile.open("input_file.txt", std::ios_base::app);
   myfile << "Writing this to a file. Test for TAU\n";
   myfile.seekp (myfile.beg + 7);
   myfile.write ("OVER",4);
   myfile.close();

   MPI_Finalize();   
   return(0);
}
