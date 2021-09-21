## Trace examples for ADIOS codes

Gathering TAU traces for IO operations (Write / Read) and the metadata operations associated with it (Open / Seek).

### Example for Open/Close for Write

Code
```c++
adios2::ADIOS adios(MPI_COMM_WORLD);
adios2::IO bpIO = adios.DeclareIO("WriteBP");
adios2::Engine bpFileWriter = bpIO.Open("input_file", adios2::Mode::Write);
bpFileWriter.Close();
```

TAU logs created with `-io -skel`
```
{"ts": 1630435888978714, "dur": 280, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "open", "args": {"pathname": "input_file/md.0", "flags": 577, "mode": 438}, "return": 22},
{"ts": 1630435888978716, "dur": 313, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "open", "args": {"pathname": "input_file/md.idx", "flags": 577, "mode": 438}, "return": 23},
{"ts": 1630435888978640, "dur": 419, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "open", "args": {"pathname": "input_file/data.0", "flags": 577, "mode": 438}, "return": 20},
{"ts": 1630435888978709, "dur": 384, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "open", "args": {"pathname": "input_file/.bpversion", "flags": 577, "mode": 438}, "return": 21},
{"ts": 1630435888979454, "dur": 6, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "lseek", "args": {"fd": 21, "offset": 0, "whence": 1}, "pathname": "input_file/.bpversion", "return": 0},
{"ts": 1630435888979464, "dur": 130, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "write", "args": {"fd": 21, "buf": "0x7fffd759cd80", "count": 1 }, "pathname": "input_file/.bpversion", "return": 1},
{"ts": 1630435888979603, "dur": 19, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "close", "args": {"fd": 21}, "pathname": "input_file/.bpversion", "return": 0},
{"ts": 1630435888979712, "dur": 5, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "lseek", "args": {"fd": 20, "offset": 0, "whence": 1}, "pathname": "input_file/data.0", "return": 0},
{"ts": 1630435888979721, "dur": 90, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "write", "args": {"fd": 20, "buf": "0x1c900050", "count": 131 }, "pathname": "input_file/data.0", "return": 131},
{"ts": 1630435888980009, "dur": 9, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "close", "args": {"fd": 20}, "pathname": "input_file/data.0", "return": 0},
{"ts": 1630435888980152, "dur": 4, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "lseek", "args": {"fd": 22, "offset": 0, "whence": 1}, "pathname": "input_file/md.0", "return": 0},
{"ts": 1630435888980159, "dur": 79, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "write", "args": {"fd": 22, "buf": "0x1c90a500", "count": 135 }, "pathname": "input_file/md.0", "return": 135},
{"ts": 1630435888980265, "dur": 4, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "lseek", "args": {"fd": 23, "offset": 0, "whence": 1}, "pathname": "input_file/md.idx", "return": 0},
{"ts": 1630435888980272, "dur": 67, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "write", "args": {"fd": 23, "buf": "0x1c8cf870", "count": 128 }, "pathname": "input_file/md.idx", "return": 128},
{"ts": 1630435888980396, "dur": 131, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "fopen64", "args": {"path": "input_file/profiling.json", "mode": "wb"}, "return": "0x1c90adf0"},
{"ts": 1630435888980538, "dur": 73, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "write", "args": {"fd": 20, "buf": "0x1c98c920", "count": 388 }, "pathname": "input_file/profiling.json", "return": 388},
{"ts": 1630435888980636, "dur": 10, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "fclose", "args": {"fp": "0x1c90adf0"}, "return": 0, "pathname": "input_file/profiling.json"},
{"ts": 1630435888980651, "dur": 3, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "lseek", "args": {"fd": 23, "offset": 38, "whence": 0}, "pathname": "input_file/md.idx", "return": 38},
{"ts": 1630435888980657, "dur": 37, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "write", "args": {"fd": 23, "buf": "0x7fffd759d0f0", "count": 1 }, "pathname": "input_file/md.idx", "return": 1},
{"ts": 1630435888980697, "dur": 10, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "lseek", "args": {"fd": 23, "offset": 0, "whence": 2}, "pathname": "input_file/md.idx", "return": 128},
{"ts": 1630435888980710, "dur": 7, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "close", "args": {"fd": 22}, "pathname": "input_file/md.0", "return": 0},
{"ts": 1630435888980720, "dur": 8, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "close", "args": {"fd": 23}, "pathname": "input_file/md.idx", "return": 0},
```

**With a Put**

Code that is added between the open/close sequence.
```c++
const std::string myString("Hello Variable String");
adios2::Variable<std::string> bpString =
            bpIO.DefineVariable<std::string>("bpString");
bpFileWriter.Put(bpString, myString);
```

The logs show the same patterns for all files, the amount of data written for `md.idx` remains the same. The others write more data.

```
{"ts": 1630445604556460, "dur": 92, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "write", "args": {"fd": 20, "buf": "0x28890050", "count": 197 }, "pathname": "input_file/data.0", "return": 197},
{"ts": 1630445604556924, "dur": 89, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "write", "args": {"fd": 23, "buf": "0x280319b0", "count": 227 }, "pathname": "input_file/md.0", "return": 227},

{"ts": 1630445604558647, "dur": 66, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "write", "args": {"fd": 20, "buf": "0x289d0050", "count": 393 }, "pathname": "input_file/profiling.json", "return": 393},
```

### Open/Close for Read

Code
```c++
    adios2::ADIOS adios(MPI_COMM_WORLD);
    adios2::IO bpIO = adios.DeclareIO("WriteBP");
    adios2::Engine bpReader = bpIO.Open("input_file", adios2::Mode::Read);
    bpReader.Close();
```

TAU logs created with `-io -skel`
```
{"ts": 1630448893932662, "dur": 28422, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "open", "args": {"pathname": "input_file/.bpversion", "flags": 0, "mode": 511}, "return": 19},
{"ts": 1630448893961130, "dur": 4, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "lseek", "args": {"fd": 19, "offset": 0, "whence": 0}, "pathname": "input_file/.bpversion", "return": 0},
{"ts": 1630448893961137, "dur": 41, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "read", "args": {"fd": 19, "buf": 0x7ffff581f1c0, "count": 1}, "pathname": "input_file/.bpversion", "return": 1},
{"ts": 1630448893961181, "dur": 16, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "close", "args": {"fd": 19}, "pathname": "input_file/.bpversion", "return": 0},
{"ts": 1630448893961269, "dur": 1050, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "open", "args": {"pathname": "input_file/md.idx", "flags": 0, "mode": 511}, "return": 19},
{"ts": 1630448893962338, "dur": 952, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "open", "args": {"pathname": "input_file/md.0", "flags": 0, "mode": 511}, "return": 20},
{"ts": 1630448893963380, "dur": 4, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "lseek", "args": {"fd": 19, "offset": 0, "whence": 0}, "pathname": "input_file/md.idx", "return": 0},
{"ts": 1630448893963387, "dur": 33, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "read", "args": {"fd": 19, "buf": 0x216007a0, "count": 128}, "pathname": "input_file/md.idx", "return": 128},
{"ts": 1630448893963426, "dur": 2, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "lseek", "args": {"fd": 20, "offset": 0, "whence": 0}, "pathname": "input_file/md.0", "return": 0},
{"ts": 1630448893963431, "dur": 22, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "read", "args": {"fd": 20, "buf": 0x21986e90, "count": 227}, "pathname": "input_file/md.0", "return": 227},
{"ts": 1630448893963601, "dur": 9, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "close", "args": {"fd": 20}, "pathname": "input_file/md.0", "return": 0},
{"ts": 1630448893963823, "dur": 9, "ph": "X", "tid": 0, "pid": 0, "step": 0, "cat": "POSIX", "name": "close", "args": {"fd": 19}, "pathname": "input_file/md.idx", "return": 0},
```

**With a Get**

Code that is added between the open/close sequence.
```c++
    std::string myString;
    adios2::Variable<std::string> bpString =
             bpIO.InquireVariable<std::string>("bpString");
    bpReader.Get<std::string>(bpString, myString);
```

TAU logs are the same. This is because the file is read on open, in which case Get will only move data to buffers but will not touch the file.
