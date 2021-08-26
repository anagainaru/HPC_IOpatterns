# Trace examples for simple codes 

Gathering TAU traces for Open / Write / Read.

## Open

C type code using POSIX.
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

C++ type code using Fstream (POSIX underneath).
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
In both cases: {"ts": 1629924164199334, "dur": 14, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "fclose", "args": {"fp": "0x25c1eeb0"}, "return": 0, "pathname": "input_file.txt"},
```

## Write

In addition to the code above, there's a line to write data to the open file.
```c++
myfile << "Writing this to a file. Test for testing TAU\n";
```

**TAU log**
```yaml
{"ts": 1629992369114288, "dur": 113, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "write", "args": {"fd": 19, "buf": "0x1a6b0050", "count": 45 }, "pathname": "input_file.txt", "return": 45},
```

```
(base) bash-4.4$ ls -lah input_file.txt
-rw------- 1 againaru csc143 45 Aug 26 14:18 input_file.txt
```

## Read

```c++
#include <mpi.h>
#include <iostream>
#include <fstream>
using namespace std;

int main (int argc, char *argv[]) {
  MPI_Init(&argc, &argv);

  int length = 10;
  char * buffer = new char [length];
  std::ifstream myfile("input_file.txt", std::ifstream::binary);
  if (is) {
    myfile.read (buffer,length);
  }
  myfile.close();

  MPI_Finalize();
  return(0);
}
```

**TAU log**
```yaml
{"ts": 1630002800182612, "dur": 25, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "read", "args": {"fd": 19, "buf": 0x134d5fe0, "count": 8191}, "pathname": "input_file.txt", "return": 13},
```

```
(base) bash-4.4$ cat input_file.txt
Test for TAU
(base) bash-4.4$ jsrun -n 1 tau_exec -T mpi -io -skel ./simple.read
Test for TAU
[againaru@login1.summit build]$ ls -lah input_file.txt
-rw-rw-r-- 1 againaru csc143 13 Aug 26 14:32 input_file.txt
```
