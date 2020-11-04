## Brief Statistics

|  | LAMMPS  | NWChem | WarpX | XCG | GTC | 
|---|---|---|---|---|---|
| Total ranks  | 1  | 224  | 12  | | |
| IO types | POSIX / STDIO  | POSIX / STDIO  | POSIX / STDIO  | | |
| FS type | NFS / GPFS / Unknown  | GPFS / Unknown  | GPFS / Unknown  | | |
| # ranks involved  | 1  | 224  |  12 |   | |
| # files accesses |  11 | 468  |  Depending on test <br/> (see bellow) |   | |
| Access size (bytes) | POSIX: 697 <br/> STDIO: 453 | POSIX: 37034 <br/> STDIO: 414 | Depending on test <br/> (see bellow)  |  | |

## WarpX different tests

|  | Collision  | Laser Acc | Plasma Acc | Uniform Plasma |
|---|---|---|---|---|
| # files accesses |  530 | 62  |  1272 | 482  |
| Access size (bytes) | POSIX: 12491 <br/> STDIO: 27254 | POSIX: 6261 <br/> STDIO: 3607 | POSIX: 74286<br/>  STDIO: 58546 | POSIX: 35118<br/> STDIO: 24874 |
