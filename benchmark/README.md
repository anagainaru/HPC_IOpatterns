# IO benchmark

[benchmark design](docs/benchmark.png)

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

