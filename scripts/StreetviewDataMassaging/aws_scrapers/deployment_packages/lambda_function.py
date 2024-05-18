### Author: Ashlynn Wimer
### Date: 5/16/2024
### About: Lambda function which is used to retrieve images from Google Streetview.

from io import BytesIO
import boto3
import requests
import logging

METADATA_URL = 'https://maps.googleapis.com/maps/api/streetview/metadata?'
IMAGE_URL = 'https://maps.googleapis.com/maps/api/streetview?'
IMG_SIZE = (600, 400)
BUCKET = 'chicago-places-buckette'


def generate_request_url(loc: tuple, API_KEY: str, heading: int, metadata: bool=True) -> str:
    '''
    Generate the Streetview API request for a given location. Returns a
    metadata request if meta = True, otherwise returns the image API url.
    '''
    
    size_rq = f'size={IMG_SIZE[0]}x{IMG_SIZE[1]}'
    heading_rq = f'heading={heading}'
    key_rq = f'key={API_KEY}'
    source_rq = 'source=outdoor'
    return_error_code_rq = f'return_error_code=true'
    loc_rq = f'location={loc[0]}, {loc[1]}'

    parameters = f'{size_rq}&{heading_rq}&{source_rq}&{return_error_code_rq}&{key_rq}&{loc_rq}'

    if metadata:
        return f'{METADATA_URL}{parameters}'

    return f'{IMAGE_URL}{parameters}'
    
def is_valid_call(loc: tuple, API_KEY: str, heading: int) -> bool:
    '''
    Double check that the requested call is viable.
    If not, return False.
    '''

    metadata_url = generate_request_url(loc, API_KEY, heading, True)
    metadata = requests.get(metadata_url).json()

    if metadata['status'] == 'OK':
        return True
    
    return False

def get_image(loc: tuple, API_KEY: str, heading: int) -> BytesIO:
    '''
    Given a single coordinate, attempt to grab the image at that location
    and return it as a BytesIO object. 
    '''

    url = generate_request_url(loc, API_KEY, heading, False)
    resp = requests.get(url)    
    
    return BytesIO(resp.content)
    
# Image upload code partially scribbed from
# https://stackoverflow.com/a/76593762
def lambda_handler(event, context):
    '''
    Handle the lambda call by grabbing an image and sending it to
    S3
    '''
    
    for req in event:
        try:
            loc = (req['latitude'], req['longitude'])
            API_KEY = req['API_KEY']
            heading = req['heading']
            key = req['ID']

            # Double check our call is valid; if not, return 400. 
            if not is_valid_call(loc, API_KEY, heading):
                logging.warn(f'Skipping image with ID {req["ID"]} as we cannot verify it.')
                continue

            image_bytes = get_image(loc, API_KEY, heading)

            s3_client = boto3.client('s3')
            s3_resource = boto3.resource('s3')

            s3_client.upload_fileobj(
                Fileobj=image_bytes,
                Bucket=BUCKET,
                Key=key,
                ExtraArgs={'ContentType':'image/png'},
                Callback=None,
                Config=None
            )

            # We're not intentionally rate limiting (which is a little
            # impolite for Google), so we can at least be slightly
            # polite by waiting for processes like this to finish.
            s3_resource.Object(BUCKET, key).wait_until_exists()
        except Exception as e:
            logging.warn(f'Hit exception {e} on image {req.ID}. Continuing to next row.')
            continue