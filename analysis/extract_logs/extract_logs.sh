#!/bin/bash
module load darshan-util

app=$1
mkdir logs_${app}
for j in {1..12}; do 
	echo "/gpfs/alpine/darshan/summit/2020/$j"
	echo "---"
	for i in /gpfs/alpine/darshan/summit/2020/${j}/*/*_${app}_*; do
		ls $i
		if [ $? -eq 0 ]; then
			filename=$(basename -- "$i")
			extension="${filename##*.}"
			filename="${filename%.*}"
			darshan-parser --file $i > logs_${app}/${filename}.log
			darshan-parser $i >> logs_${app}/${filename}.log
		else
    			continue
		fi
	done
done
