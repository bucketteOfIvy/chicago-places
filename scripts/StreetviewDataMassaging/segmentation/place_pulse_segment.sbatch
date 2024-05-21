#!/bin/bash

#SBATCH --job-name=wimer_chicago_places_segment
#SBATCH --output=segmentation.out
#SBATCH --error=segmentation.err
#SBATCH --ntasks=1
#SBATCH --partition=gpu
#SBATCH --account=macs30123
#SBATCH --gres=gpu:1
#SBATCH --mem-per-cpu=32GB


module load python

python3 place_pulse_segment.py
