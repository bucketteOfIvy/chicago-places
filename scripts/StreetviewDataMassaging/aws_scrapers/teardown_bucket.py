### Author: Ashlynn Wimer
### Date: 5/17/2024
### About: This script tears down our AWS S3 bucket. It should only be called after
###        the images stored on the bucket have been moved elsewhere for more permanent
###        storage (e.g. to UChicago Box).

import boto3

BUCKET = 'chicago-places-buckette'

if __name__ == "__main__":

    double_check = input(f'This is a potentially dangerous action, and will result in the loss of all data currently stored on the S3 bucket {BUCKET}. Are you sure you want to delete the bucket? [y/N]')
    if double_check == 'y':
        print('Deleting all items in the bucket...')
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(BUCKET)
        bucket.objects.all().delete()

        print("Deleting the bucket...")
        bucket_client = boto3.client('s3')
        bucket_client.delete_bucket(Bucket=BUCKET)
        print('Done!')
        exit(0)
    
