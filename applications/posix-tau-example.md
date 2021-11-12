# Trace examples for simple codes 

Gathering TAU traces for IO operations (Write / Read) and the metadata operations associated with it (Open / Seek).

## Example with all types of operations

```cpp
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

    if (myfile)
      std::cout << "all characters read successfully.";
    else
      std::cout << "error: only " << myfile.gcount() << " could be read";
    myfile.close();

    // ...buffer contains the entire file...
    delete[] buffer;
  }
  MPI_Finalize();
  return 0;
}
```

The file read has 45 Bytes and the write is being done on stdout.
```
(base) bash-4.4$ ls -lah input_file.txt
-rw-rw-r-- 1 againaru csc143 45 Aug 26 16:10 input_file.txt
```

The TAU2 skel log generated contains the following lines:
```yaml
[
{"ts": 1630009505960310, "dur": 179, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "fopen64", "args": {"path": "input_file.txt", "mode": "rb"}, "return": "0x1c5f9b50"},
{"ts": 1630009505960499, "dur": 12, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "lseek64", "args": {"fd": 19, "offset": 0, "whence": 2}, "pathname": "input_file.txt", "return": 45},
{"ts": 1630009505960515, "dur": 3, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "lseek64", "args": {"fd": 19, "offset": 0, "whence": 1}, "pathname": "input_file.txt", "return": 45},
{"ts": 1630009505960520, "dur": 3, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "lseek64", "args": {"fd": 19, "offset": 0, "whence": 0}, "pathname": "input_file.txt", "return": 0},
{"ts": 1630009505960527, "dur": 26, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "read", "args": {"fd": 19, "buf": 0x1cd75fe0, "count": 8191}, "pathname": "input_file.txt", "return": 45},
{"ts": 1630009505960558, "dur": 23, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "fwrite", "args": {"ptr": "0x100014b8", "size": 1, "nmemb": 33, "stream": "0x200001241790"}, "pathname": "stdout", "return": 33},
{"ts": 1630009505960584, "dur": 12, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "fclose", "args": {"fp": "0x1c5f9b50"}, "return": 0, "pathname": "input_file.txt"},
{"ts": 1630009505960629, "dur": 1, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "TAU", "name": "program exit"}
```

## IO Operations
### Write

Using fstream, adding the line to write data to the open file.
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

### Read

```c++
  int length = 10;
  char * buffer = new char [length];
  if (myfile) {
    myfile.read (buffer,length);
  }
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
Test for T
[againaru@login1.summit build]$ ls -lah input_file.txt
-rw-rw-r-- 1 againaru csc143 13 Aug 26 14:32 input_file.txt
```

For multiple reads one after another (reading each time from the beginning of the file, first the total length of the file and second only half)
```
{"ts": 1630011948409652, "dur": 28, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "read", "args": {"fd": 19, "buf": 0x3a515fe0, "count": 8191}, "pathname": "input_file.txt", "return": 45},
{"ts": 1630011948409688, "dur": 12, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "read", "args": {"fd": 19, "buf": 0x3a515fe0, "count": 8191}, "pathname": "input_file.txt", "return": 45},
```
The return is always the total size of the file (maybe of the minimum read block defined by the FS)

For multiple writes one after another (regardless of the seekp location) the return will be the amount of bytes sucessfully written:
```
{"ts": 1630014367714588, "dur": 4557, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "write", "args": {"fd": 19, "buf": "0x118f5fe0", "count": 37 }, "pathname": "input_file.txt", "return": 37},
{"ts": 1630014367719156, "dur": 24, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "write", "args": {"fd": 19, "buf": "0x118f5fe0", "count": 4 }, "pathname": "input_file.txt", "return": 4},
```


## Metadata (Open)

C++ type code using Fstream (POSIX underneath).
```cpp
   myfile.open("input_file.txt");
   myfile.close();
```

**TAU log**
```yaml
Pure POSIX: {"ts": 1629924164198789, "dur": 536, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "fopen", "args": {"path": "input_file.txt", "mode": "r"}, "return": "0x25c1eeb0"},
Fstream: {"ts": 1629992369114072, "dur": 206, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "fopen64", "args": {"path": "input_file.txt", "mode": "w"}, "return": "0x19c996f0"},
In both cases: {"ts": 1629924164199334, "dur": 14, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "fclose", "args": {"fp": "0x25c1eeb0"}, "return": 0, "pathname": "input_file.txt"},
```
