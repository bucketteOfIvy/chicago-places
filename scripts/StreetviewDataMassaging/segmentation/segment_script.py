# pip install yacs 2>&1 >> install.log
# git init 2>&1 >> install.log
# git remote add origin https://github.com/CSAILVision/semantic-segmentation-pytorch.git 2>> install.log
# git pull origin master 2>&1 >> install.log
# DOWNLOAD_ONLY=1 .demo/test.sh 2>> install.log

import logging
import scipy.io
import torchvision.transforms
import torch
import numpy as np
import pandas
import csv
import os

import PIL
from PIL import Image
import zipfile

from mit_semseg.models import ModelBuilder, SegmentationModule
from mit_semseg.utils import colorEncode


### Get names
colors = scipy.io.loadmat('../../../data/segmentation/color150.mat')['colors']
names = {}
with open('../../../data/segmentation/object150_info.csv') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        names[int(row[0])] = row[5].split(';')[0]

### Load in the actual model
net_encoder = ModelBuilder.build_encoder(
    arch='resnet50dilated',
    fc_dim=2048,
    weights='ckpt/ade20k-resnet50dilated-ppm_deepsup/encoder_epoch_20.pth'
)

net_decoder = ModelBuilder.build_decoder(
    arch='ppm_deepsup',
    fc_dim=2048,
    num_class=150,
    weights='ckpt/ade20k-resnet50dilated-ppm_deepsup/decoder_epoch_20.pth',
    use_softmax=True
)

crit = torch.nn.NLLLoss(ignore_index=-1)
segmentation_module=SegmentationModule(net_encoder, net_decoder, crit)
segmentation_module.eval()
segmentation_module.cuda()

### Transform for normalizing our images
pil_to_tensor = torchvision.transforms.Compose([
    torchvision.transforms.ToTensor(),
    torchvision.transforms.Normalize(
        # According to the DemoSegmenter script,
        # these are average mean+std "across a 
        # large photo dataset." So, I'll, uh, take 
        # them at their word.
        mean=[0.485, 0.456, .406],
        std=[0.229, 0.224, 0.225]
    )
])

### Set up our test image
#pil_image = Image.open('../../../data/images/I1.png').convert('RGB')
#img_orig = np.array(pil_image)
#img_data = pil_to_tensor(img_orig)
#singleton_batch = {'img_data': img_data[None].cuda()}
#output_size = img_data.shape[1:]

SUPERBATCH_SIZE = 2500
SUPERBATCH_N = 10
for superbatch in range(SUPERBATCH_N):
    logging.info(f'Starting superbatch number {superbatch}')

    image_datums = []
    filenames = []
    low = superbatch * SUPERBATCH_SIZE
    upper = min((superbatch + 1) * SUPERBATCH_SIZE, len(os.listdir()))
    for f in os.listdir('../../../data/images/')[low:upper]:
        pil_image = Image.open(f'../../../data/images/{f}').convert('RGB')
        image_original = np.array(pil_image)
        image_data = pil_to_tensor(image_original)
        image_datums.append(image_data)
        filenames.append(f)

    batch = {'img_data': torch.stack(image_datums).cuda()}
    output_size = image_data.shape[1:]

    ### Run model
    with torch.no_grad():
        scores = segmentation_module(batch, segSize=output_size)

    ### Get predicted results
    _, preds = torch.max(scores, dim=1)

    ### Save our result
    df = []
    for pred in preds:
        unique, counts = np.unique(np.array(pred.cpu()), return_counts=True)
        
        named_counts = {}
        for u, c in zip(unique, counts):
            named_counts[u] = c

        for i, _ in enumerate(names):
            if i not in named_counts.keys():
                named_counts[i] = 0

        neat = sorted(named_counts.items(), key=lambda x: x[0])
        df.append([y for x, y in neat])

    if superbatch == 0:
        df = pandas.DataFrame(np.array(df).T, index=names.values(), columns=filenames)
        continue

    pandas.concat(
        [
            pandas.read_parquet('../../../data/raw/streetview_segments.parquet'),
            pandas.DataFrame(np.array(df).T, index=names.values(), columns=filenames)
        ]
    ).to_parquet('../../../data/raw/streetview_segments.parquet')
