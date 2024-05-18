### Author: Ashlynn Wimer
### Date: 5/16/2024
### About: This script prepares the metadata location file for our scraper by
###        verifying image availability, generating random headings, and finding
###        image dates.

import pandas as pd
import numpy as np
import requests
import os

METADATA_URL = 'https://maps.googleapis.com/maps/api/streetview/metadata?'
API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY_CHICAGO')

def generate_request_url(loc: tuple, heading: int) -> str:
    '''
    Generate the Streetview Metadata API request for a given location.
    '''
    size_rq = f'size=600x400'
    heading_rq = f'heading={heading}'
    key_rq = f'key={API_KEY}'
    source_rq = 'source=outdoor'
    return_error_code_rq = f'return_error_code=true'
    loc_rq = f'location={loc[0]}, {loc[1]}'

    parameters = f'{size_rq}&{heading_rq}&{source_rq}&{return_error_code_rq}&{key_rq}&{loc_rq}'

    return f'{METADATA_URL}{parameters}'
    
if __name__ == "__main__":
    
    df = pd.read_csv('../../data/shapes/streetview_locations_initial.csv')

    print("Going through the initial dataframe for valid locations.")
    # This is maybe a slightly messay approach, but it works.
    lons, lats, ids, status, headings, dates = [], [], [], [], [], []
    for i, row in df.iterrows():

        if i % 100 == 0:
            print(f'At row {i}.')

        heading = np.random.randint(0, 360)
        locs = (row['latitude'], row['longitude'])    
        metadata = requests.get(generate_request_url(locs, heading)).json()

        if metadata['status'] != 'OK':
            headings.append(heading)
            status.append(metadata['status'])
            dates.append('NA')
            lons.append('NA')
            lats.append('NA')
            ids.append(row['ID'])
            continue
        
        headings.append(heading)
        status.append(metadata['status'])
        dates.append(metadata['date'])
        ids.append(row['ID'])
        lons.append(metadata['location']['lng'])
        lats.append(metadata['location']['lat'])

    new_df = pd.DataFrame(
        {
            'ID':ids,
            'longitude':lons,
            'latitude':lats,
            'heading':headings,
            'dates':dates,
            'status':status            
        }
    )
    
    print('Saving new_df')
    print(f'As a useful statistic, have some value counts:\n{new_df.status.value_counts()}')

    new_df.to_csv('../../data/shapes/streetview_metadata_and_locs.csv', index=False)

