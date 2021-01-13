# Analyzing the IO logs

Two step analysis:
  - Extract the list of features from the raw Darshan logs
  - Create clusters with applications with similar patterns

## Extract the feature list

### 1. Extract the list of applications

List of applications that generated the Darshan logs we will analyze. The list of application will be annotated by the field it is part of (example XGC is fusion, CANDLE is AI etc).

For Summit application, the `extract_job_info.sh` script is used to extract the list of applications.

### 2. Parse all the darshan logs

And create a log that follows the format needed by the python scripts used to extract features.
For Summit, we use the `extract_logs.sh` script to extract all the darshan logs in a given timeframe and containing a keyword (either application name or user or none).
In the current configuration, the script extracts all the logs between September and December for user againaru.

The darshan files need to be parsed with the `--file` option followed by the default option in order to be usable by the python scripts:

```bash
darshan-parser --file ${darshan_log} > logs/${filename}.log
darshan-parser ${darshan_log} >> logs/${filename}.log
```

### 3. Extract the list features

From each darshan log and store them in the same file.

```bash
for i in logs/*.log; do
    python extract_feature_list.py $i summit_againaru_features.csv; 
done
```

