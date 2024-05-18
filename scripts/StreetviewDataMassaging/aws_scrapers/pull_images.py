### Author: Ashlynn Wimer
### Date: 5/17/2024
### About: This script calls a set of lambda functions which retrieve images
###        from the Google Streetview API and saves them into an S3 bucket. 

import pandas as pd
import numpy as np
import json
import boto3
import os

LAMBDA_FUNCTION_NAME = 'scrape_image'
STEP_FUNCTION_NAME = 'chicago-places-state-machine'
API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY_CHICAGO')

def generate_request_batches(df: pd.DataFrame, n_batches: int=10) -> list:
    '''
    Generate n_batches of JSONs containing n_int requests for our lambda requests. 
    '''

#    assert rows_per_batch * n_batches <= len(df), 'DataFrame must have fewer rows than the number of requested batches.'

    dfs = [pd.DataFrame(x) for x in np.array_split(df, n_batches)]

    batches = []
    for df in dfs:
        requests = []
        for _, row in df.iterrows():
            requests.append(
                {
                    'ID':row['ID'],
                    'latitude':row['latitude'],
                    'longitude':row['longitude'],
                    'heading':row['heading'],
                    'API_KEY':API_KEY
                }
            )
        batches.append(requests)
    
    return batches

if __name__ == '__main__':    
    df = pd.read_csv('../../../data/shapes/streetview_metadata_and_locs.csv')
    
    df = df[df['status'] == 'OK']
    print(f'Setting up step function for {len(df)} entries...')

    # We do this 10 big batches at a time, or else AWS get's mad.

    tnth_of_entries = len(df) // 100
    for super_batch in range(101):
        print(f'Starting super batch {super_batch}.')
        start = super_batch * tnth_of_entries
        end = min((super_batch + 1) * tnth_of_entries, len(df))
        mini_df = df[start : end]

        # Try this out with *very* few rows. 
        request_batches = generate_request_batches(mini_df, 10)

        sfn = boto3.client('stepfunctions')
        iam_client = boto3.client('iam')
        
        response = sfn.list_state_machines()
        state_machine_arn = [sm['stateMachineArn'] for sm in response['stateMachines']
                            if sm['name'] == STEP_FUNCTION_NAME][0]
        
        response = sfn.start_sync_execution(
            stateMachineArn=state_machine_arn,
            name=STEP_FUNCTION_NAME,
            input=json.dumps(request_batches)
        )
