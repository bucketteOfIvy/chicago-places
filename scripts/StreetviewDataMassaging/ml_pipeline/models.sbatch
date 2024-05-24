#!/bin/bash

#SBATCH --job-name=chicago-places-ml
#SBATCH --output=spark.out
#SBATCH --error=spark.err
#SBATCH --ntasks=8
#SBATCH --partition=caslake
#SBATCH --account=macs30123
#SBATCH --mem-per-cpu=1GB

module load python spark

export PYSPARK_DRIVER_PYTHON=/software/python-anaconda-2022.05-el8-x86_64/bin/python3

spark-submit --master local[*] --driver-memory 5G models.py

# to filter out logging messages from output, run the following:
cat spark.out | grep -vE "INFO|WARN"
