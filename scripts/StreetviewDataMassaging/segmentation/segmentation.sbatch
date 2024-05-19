#!/bin/bash

#SBATCH --job-name=wimer_chicago_places_segment
#SBATCH --output=segmentation.out
#SBATCH --error=segmentation.err
#SBATCH --ntasks=1
#SBATCH --partitions=ssd-gpu
#SBATCH --account=ssd
#SBATCH --gres=gpu:1
#SBATCH --mem-per-cpu=32GB
#SBATCH --qos=ssd

module load python

python3 segment_script.py
