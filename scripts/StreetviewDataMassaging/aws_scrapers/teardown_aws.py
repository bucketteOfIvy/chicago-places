### Author: Ashlynn Wimer
### Date: 5/17/2024
### About: This script tears down our AWS scraping pipeline, leaving only the
###        s3 bucket. To remove the bucket, run 'teardown_bucket.py'

import boto3

LAMBDA_FUNCTION_NAME = 'scrape_image'
STEP_FUNCTION_NAME = 'chicago-places-state-machine'

if __name__ == "__main__":
    # State machine
    print('Deleting lambda...')
    aws_lambda = boto3.client('lambda')

    try:
        aws_lambda.delete_function(FunctionName = LAMBDA_FUNCTION_NAME)
        print('Lambda is gone!')
    except aws_lambda.exceptions.ResourceNotFoundException:
        print('Lambda function was already deleted or never created.')

    # Step function
    print('Deleting step function...')
    sfn = boto3.client('stepfunctions')

    response = sfn.list_state_machines()
    state_machine_arn = [sm['stateMachineArn']
                        for sm in response['stateMachines']
                        if sm['name'] == STEP_FUNCTION_NAME][0]
    
    try:
        response = sfn.delete_state_machine(
            stateMachineArn=state_machine_arn
        )
        print('Step function gone!')
    except sfn.exception.InvalidArn:
        print('Step function does not exist at this ARN or was already deleted.')