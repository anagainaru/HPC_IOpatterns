# Analyzing the IO logs

Two step analysis:
  - Extract the list of features from the raw Darshan logs
  - Create clusters with applications with similar patterns

**Required packages to test the scripts in this repo**

 - For plotting: python package `seaborn`
 - For feature extraction: python package `lightgbm`
 - For extracting the distance matrix: python packages `sklearn`, `dataset`, `hdbscan`
 - For the feature importance list: `libomp` and python package `xgboost`
 
All the dependencies with their versions are written in `requirements.txt`.
To install them, you will need `pip`. Run `pip install -r requirements.txt`.

## Extract the feature list

### 1. Extract the list of applications

Scripts available in folder `extract_logs`.

List of applications that generated the Darshan logs we will analyze. The list of application will be annotated by the field it is part of (example XGC is fusion, CANDLE is AI etc).

For Summit application, the `extract_job_info.sh` script is used to extract the list of applications.

### 2. Parse all the darshan logs

Scripts available in folder `extract_logs`.

And create a log that follows the format needed by the python scripts used to extract features.
For Summit, we use the `extract_logs.sh` script to extract all the darshan logs in a given timeframe and containing a keyword (either application name or user or none).
In the current configuration, the script extracts all the logs between September and December for user againaru.

The darshan files need to be parsed with the `--file` option followed by the default option in order to be usable by the python scripts:

```bash
darshan-parser --file ${darshan_log} > logs/${filename}.log
darshan-parser ${darshan_log} >> logs/${filename}.log
```

### 3. Extract the list features

Scripts available in folder `features`.

Extract features from each darshan log and store them in the same file.

```bash
for i in logs/*.log; do
    python extract_feature_list.py $i summit_againaru_features.csv; 
done
```

There are currently 161 features (including the user submitting the application, the name of the application and of the executable).
List of all the features and explanation of what each represents can be dound in the file `feature.description`.

The output file is a CSV file containing one entry for each darshan log.

## Create clusters of similar data

Scripts available in folder `clustering`.

Applications are clustered based on their features (except the app name and user name features) using hdbscan.HDBSCAN ([Link](https://hdbscan.readthedocs.io/)).
HDBSCAN is a clustering algorithm that extends DBSCAN by converting it into a hierarchical clustering algorithm, and then using a technique to extract a flat clustering based in the stability of clusters. A detailed explanation of how clustered are being formed can be found [here](https://hdbscan.readthedocs.io/en/latest/how_hdbscan_works.html).

Example results for the clustering method for the list of application runs (and darshan logs) from this repo.


![Hierarchical clustering](docs/cluster_tree.png)


### 1. Exstract the list of applications in each clusters

The script in `extract_clusters.py` creates the figure on the left. It uses hdbscan to create the cluster hierarchy then it identifies each entry in the features file that corresponds to each cluster and saves it in a file. The script saves the main clusters from the level with the stable clusters from the condensed tree (dashed line in the figure) in `*.0.csv`. The file contains one line for each entry in the features file with an additional column (`Cluster`) with labels from 0 to n-1, where n is the number of identified clusters.

The script also saves information about the two clusters created at each split, one file for each split distance (binary labels only for the dataset involved in the split). For example for the first split the file will contain all the application runs with their features and an additional column (`Cluster`) that takes values 0 (for the apps that are classified on the left side) and 1 for the right side. 

### 2. Create the distance matrix

The script in `extract_clusters.py` creates the figure on the right. It creates the clusters using hdbscan, identifies the 6 more frequently ran applications and computes the manhatten and euclidean distances between all these application runs. The script output the figure.

### 3. Feature importance
