#!/bin/bash
module load darshan-util

mkdir logs_againaru
for j in {9..12}; do 
	echo "/gpfs/alpine/darshan/summit/2020/$j"
	echo "---"
	for i in /gpfs/alpine/darshan/summit/2020/${j}/*/*againaru*; do
		ls $i
		if [ $? -eq 0 ]; then
			filename=$(basename -- "$i")
			extension="${filename##*.}"
			filename="${filename%.*}"
			darshan-parser --file $i > logs_againaru/${filename}.log
			darshan-parser $i >> logs_againaru/${filename}.log
		else
    			continue
		fi
	done
done
