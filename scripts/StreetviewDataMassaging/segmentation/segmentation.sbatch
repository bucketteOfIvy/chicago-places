#!/bin/bash

#SBATCH --job-name=wimer_chicago_places_segment
#SBATCH --output=segmentation.out
#SBATCH --error=segemntation.err
#SBATCH --ntaks=1
#SBATCH --partitions=ssd-gpu
#SBATCH --account=ssd
#SBATCH --gres=gpu:1
#SBATCH --mem-per-cpu=32GB

module load python

pip install --user yacs 2>&1 >> install.log
git init 2>&1 >> install.log
git remote add origin https://github.com/CSAILVision/semantic-segmentation-pytorch.git 2 >> install.log
git pull origin master 2>&1 >> install.log
DOWNLOAD_ONLY=1 .demo/test.sh 2>> install.log

python3 segment_script.py