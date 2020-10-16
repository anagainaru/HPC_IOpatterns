/* wr_at.c
 *
 * Example to demonstrate use of MPI_File_write_at and MPI_File_read_at
 *
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "mpi.h"

#define NUM_INTS 100

void sample_error(int error, char *string){
  fprintf(stderr, "Error %d in %s\n", error, string);
  MPI_Finalize();
  exit(-1);
}

void write_to_file_mpi(MPI_File fh, int rank, int comm_size){
  int i, *buff;
  MPI_Offset disp, offset;
  MPI_Datatype etype, ftype, buftype;
  MPI_Info info;
  MPI_Status status;
  int result, count;

  /* Set the file view which tiles the file type MPI_INT, starting 
     at displacement 0. In this example, the etype is also MPI_INT */
  disp = 0;
  etype = MPI_INT;
  ftype = MPI_INT;
  info = MPI_INFO_NULL;
  result = MPI_File_set_view(fh, disp, etype, ftype, "native", info);
  if(result != MPI_SUCCESS) 
    sample_error(result, "[MPI_File_set_view] Error setting the file view");

  /* Allocate and initialize buff1 */
  buff = (int *) malloc(NUM_INTS * sizeof(int));
  for(i=0; i<NUM_INTS; i++)
		  buff[i] = i;

  /* Set the buffer type to be MPI_INT */ 
  buftype = MPI_INT;
  offset = rank * NUM_INTS;
  /* Write the buff1 starting at offset 0 (the first etype in the file) */
  result = MPI_File_write_at(fh, offset, buff, NUM_INTS, buftype, &status);
  if(result != MPI_SUCCESS) 
    sample_error(result, "[MPI_File_write_at] Error writting the buffer");
  
  MPI_Get_elements(&status, MPI_BYTE, &count);
  if(count != NUM_INTS * sizeof(int))
    fprintf(stderr, "Did not write the same number of bytes as requested\n");
  else
    fprintf(stdout, "Wrote %d bytes\n", count);

  free(buff);
}

void read_from_file_mpi(MPI_File fh, int rank, int comm_size){
  int i, *buff;
  MPI_Offset disp, offset;
  MPI_Datatype etype, ftype, buftype;
  MPI_Info info;
  MPI_Status status;
  int result, count;

  /* Allocate a buffer to read into */
  buff = (int *) malloc(NUM_INTS * sizeof(int));
  /* Set the buffer type to be MPI_INT */ 
  buftype = MPI_INT;
  offset = rank * NUM_INTS;
  /* Read NUM_INTS integers into this buffer */
  result = MPI_File_read_at(fh, offset, buff, NUM_INTS, buftype, &status); 
  if(result != MPI_SUCCESS) 
    sample_error(result, "[MPI_File_read_at] Error in reading the file");

  /* Find out how many bytes were read and compare to how many we expected */
  result = MPI_Get_elements(&status, MPI_BYTE, &count);
  if(result != MPI_SUCCESS)
    sample_error(result, "MPI_Get_elements");
  if(count != NUM_INTS * sizeof(int))
    fprintf(stderr, "Did not read the same number of bytes as requested\n");
  else
    fprintf(stdout, "Read %d bytes\n", count);
  
  /* Check if the values are correct */
  int good = 0;
  for(i=0; i<NUM_INTS; i++)
  	if(buff[i] != i){
		good = 1;
		break;
	}
  if (good)
	fprintf(stderr, "The read data is not consistent with the write data\n");
  else 
    printf("Read data contains the correct values\n");

  free(buff);
}

void write_to_file_posix(FILE *fp, char *msg){
  fprintf(fp, "%s\n", msg);
}

int main(int argc, char **argv){
  int i, rank,  comm_size;
  MPI_Offset disp, offset, file_size;
  MPI_Datatype etype, ftype, buftype;
  MPI_Info info;
  MPI_Status status;
  int result, count, differs;

  MPI_File fh; // data file
  char filename[128];
  FILE *fptr;  // management file
  char mfile[150];
  mfile[0] = '\0';
  strcat(mfile, filename);
  strcat(mfile, "_log");

  if(argc < 2) {
    fprintf(stdout, "Usage: %s filename\n", argv[0]);
    exit(-1);
  }
  strcpy(filename, argv[1]);

  MPI_Init(&argc, &argv);

  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &comm_size);

  /* Rank 0 will be responsible of writing the management file */
  if (rank == 0){
    fptr = fopen(mfile, "w");
    if (fptr == NULL) fprintf(stderr, "Error opening the management file");
  }
  /* Open the file on the communicator group MPI_COMM_WORLD
     for reading and writing */
  result = MPI_File_open(MPI_COMM_WORLD, filename, 
			 MPI_MODE_RDWR | MPI_MODE_CREATE, MPI_INFO_NULL, &fh);
  if(result != MPI_SUCCESS) 
    sample_error(result, "[MPI_File_open] Error opening file");
 
  /* Write dummy buffer to the file */
  write_to_file_mpi(fh, rank, comm_size);
  if (rank == 0) write_to_file_posix(fptr, "[log] Success write");

  /* Read data from the generated file */
  read_from_file_mpi(fh, rank, comm_size);
  if (rank == 0) write_to_file_posix(fptr, "[log] Success read");

  MPI_Barrier(MPI_COMM_WORLD);
  MPI_File_get_size(fh, &file_size);

  /* Compare the file size with what we expect */
  if(file_size != (comm_size * NUM_INTS * sizeof(int)))
    fprintf(stderr, "File size is not equal to the write size\n");
  
  if (rank == 0){
 	fclose(fptr);
  }

  result = MPI_File_close(&fh);
  if(result != MPI_SUCCESS) 
    sample_error(result, "[MPI_File_close] Error closing the file");

  MPI_Finalize();
}
