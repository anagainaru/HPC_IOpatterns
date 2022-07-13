# Time series logs

Extracted using TAU.

## Example TAU logs

For traditional HPC applications: LAMMPS, WarpX, XGC, NWChem.

For AI based applications: TIL-analysis, StemDL, FASTRAN, ImageNet.

## Compress and extend TAU logs

```bash
$ python extract_patterns_json.py -h
usage: extract_patterns_json.py [-h] [-v] [-i] [-o OUTPUT] infile req_ranks req_exec

positional arguments:
  infile                Input TAU json file
  req_ranks             Number of requested ranks
  req_exec              Requested execution time in seconds

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Print debug information
  -i, --interpolate     Repeat only log patterns that can be interpolated
  -o OUTPUT, --output OUTPUT
                        Output file to store the new JSON log
       
$ python extract_patterns_json.py lmp-water-vapour/skel10/all.trace.json 4 3600 -o lmp-water-vapour/skel10/stretch.trace.json -i
```

The routine reads the JSON file, identifies patterns and isolates the start and end patterns. This is done by select the number of pattern clusters with silhouette analysis ([Link](https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html)).
It then finds the frequent patterns based on the operation types and interpolates the behavior. It uses the interpolations to 
create a the new log based on the frequent patterns.


