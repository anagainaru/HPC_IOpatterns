#include <iostream>
#include <fstream>
#include <mpi.h>

using namespace std;

int main (int argc, char *argv[]) {

  MPI_Init(&argc, &argv);
  std::ifstream myfile("input_file.txt", std::ifstream::binary);
  if (myfile) {
    // get length of file:
    myfile.seekg (0, myfile.end);
    int length = myfile.tellg();
    myfile.seekg (0, myfile.beg);

    char * buffer = new char [length];
    myfile.read (buffer,length);
    myfile.seekg (0, myfile.beg);
    char * buffer2 = new char [length/2];
    myfile.read (buffer2,length/2);

    if (myfile)
      std::cout << "all characters read successfully.";
    else
      std::cout << "error: only " << myfile.gcount() << " could be read";
    myfile.close();

    // ...buffer contains the entire file...
    delete[] buffer;
    delete[] buffer2;
  }
  MPI_Finalize();   
  return 0;
}
