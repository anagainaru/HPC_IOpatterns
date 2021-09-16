# IO benchmark

[benchmark design](./docs/benchmark.png)

## Workflow generator

Darshan logs are used to create clusters
- Identify representative runs for the clusters (smaller possible set that covers the characteristics of the cluster)
- Re-run the representative cases with DTX activated

**Output: 2D behaviors** 
- Extend each cluster with timestamp information
- For each IO transfer, we will have some associated variability
- Depending on the degree of variability we might need to split the cluster

Based on the 2D behavior and input from the user
- Create a workload for the benchmark

## Methodology 

1. Extract I/O patterns
- Run application (default Darshan) `i`
- Create a list of features
- Detect if application `i` is using ML or not
- Create clusters of behavior for all runs of application `i`

2. Analyze 
- Place application `i` in a class. 
- Analyze the patterns of each class in relation to the others

3. Time series analysis
- TAU
- Darshan limitations
- Include more features in the analysis
