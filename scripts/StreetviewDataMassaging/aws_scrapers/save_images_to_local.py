### Author: Ashlynn Wimer
### Date: 5/17/2024
### About: This script grabs all images from our s3 bucket and saves them to a local
###        (zipped) directory.

from PIL import Image, UnidentifiedImageError
import os
import boto3


BUCKET = 'chicago-places-buckette'

if __name__ == "__main__":
    s3c = boto3.client('s3')
    s3r = boto3.resource('s3')
    bucket = s3r.Bucket(BUCKET)
    
    print('getting keys..')
    keys = []
    for obj in bucket.objects.all():
        keys.append(obj.key)

    print(f'Found {len(keys)} keys.')

    print('downloading images. this may take a while..')    
    for i, key in enumerate(keys):
        # So the user doesn't die a little waiting
        if (i % 100 == 0) and (i > 0): 
            print(f'Starting image {i}!')

        is_already_made = f'{key}.png' in os.listdir('../../../data/images/')
        if is_already_made:
            continue
        
        try:
            # Get images        
            img_bytes = s3c.get_object(Bucket=BUCKET, Key=key)
            img = Image.open(img_bytes['Body'])
            img.save(f'../../../data/images/{key}.png')
        except UnidentifiedImageError:
            print(f'Key {key} belongs to an unidentified image. Continuing-')
            continue