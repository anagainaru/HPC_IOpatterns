# Trace examples for simple codes 

## Open

**1. C type code `open`**
Code
```c
#include <stdio.h>
#include <mpi.h>

int main () {
   FILE *fp;
   MPI_Init(&argc, &argv);
   fp = fopen("input_file.txt","r");
   fclose(fp);
   MPI_Finalize();
   return(0);
}
```

**2. C++ type code `open`**
```cpp
#include <mpi.h>
#include <iostream>
#include <fstream>
using namespace std;

int main (int argc, char *argv[]) {
   ofstream myfile;
   MPI_Init(&argc, &argv);

   myfile.open("input_file.txt");
   myfile.close();
  
   MPI_Finalize();
   return(0);
}
```

**TAU log**
```yaml
Pure POSIX: {"ts": 1629924164198789, "dur": 536, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "fopen", "args": {"path": "input_file.txt", "mode": "r"}, "return": "0x25c1eeb0"},
Fstream: {"ts": 1629992369114072, "dur": 206, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "fopen64", "args": {"path": "input_file.txt", "mode": "w"}, "return": "0x19c996f0"},
{"ts": 1629924164199334, "dur": 14, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "fclose", "args": {"fp": "0x25c1eeb0"}, "return": 0, "pathname": "input_file.txt"},
```

