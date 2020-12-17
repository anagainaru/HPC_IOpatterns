#!/bin/bash

mkdir todel
for j in {1..12}; do 
	for i in {1..31}; do
		echo "/gpfs/alpine/darshan/summit/2020/$j/$i -> todel/darshan_jobs_2020_${j}_$i"
		find /gpfs/alpine/darshan/summit/2020/${j}/${i} -type f | awk -F "2020/${j}/${i}/" '{print $2}' | awk -F '_id' '{print $1}' | sort -u > todel/darshan_jobs_2020_${j}_$i 
	done
done

echo "Concatenating logs into one per month"
# filter out python, test and debug based applications
for i in {1..12}; do echo "Month $i .. done"; cat todel/darshan_jobs_2020_${i}_* | grep -iFv "python" | grep -iFv "debug" | grep -iFv "test" | sort -u > todel/darshan_jobs_2020_m$i; done

echo "Concatenating all the applications into one file"
cat todel/darshan_jobs_2020_m* | sort -u > todel/darshan_jobs_2020_all

echo "Matching username to names"
rm darshan_jobs_2020_all
while read line; do
  user=`echo $line | cut -d"_" -f1`
  job=`echo $line | cut -d"_" -f2-`
  name=`finger $user | grep Name | cut -d":" -f3`
  echo $name, $user, $job >> darshan_jobs_2020_all
done <todel/darshan_jobs_2020_all

echo "Usernames are trimmed after 8 characters, fingers will not recognize the trimmed usernames in darshan"

rm -r todel
