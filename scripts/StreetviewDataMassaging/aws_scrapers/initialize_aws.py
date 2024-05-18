### Author: Ashlynn Wimer
### Date: 5/18/2024
### About: This script initializes our lambda function, our step function, and 
###        our S3 bucket.

import boto3
import json

BUCKET = 'chicago-places-buckette'
LAMBDA_FUNCTION_NAME = 'scrape_image'
STEP_FUNCTION_NAME = 'chicago-places-state-machine'

def make_def(lambda_arn: str) -> dict:
    '''
    Make the definition for our step function.
    '''
    definition = {
      "Comment": "Chicago Places Streetview Scrape Machine",
      "StartAt": "Map",
      "States": {
        "Map": {
          "Type": "Map",
          "End": True,
          "MaxConcurrency": 10,
          "Iterator": {
            "StartAt": "Lambda Invoke",
            "States": {
              "Lambda Invoke": {
                "Type": "Task",
                "Resource": "arn:aws:states:::lambda:invoke",
                "OutputPath": "$.Payload",
                "Parameters": {
                  "Payload.$": "$",
                  "FunctionName": lambda_arn
                },
                "Retry": [
                  {
                    "ErrorEquals": [
                      "Lambda.ServiceException",
                      "Lambda.AWSLambdaException",
                      "Lambda.SdkClientException",
                      "Lambda.TooManyRequestsException",
                      "States.TaskFailed",
                      "Lambda.Unknown"                      
                    ],
                    "IntervalSeconds": 2,
                    "MaxAttempts": 1,
                    "BackoffRate": 2
                  }
                ],
                "End": True
              }
            }
          }
        }
      }
    }
    return definition

if __name__ == "__main__":

    #### Setup our lambda function. ####
    print('Setting up lambda...')

    aws_lambda = boto3.client('lambda')
    iam = boto3.client('iam')
    role = iam.get_role(RoleName='LabRole')

    with open('deployment_packages/chicago-places-deployment-package.zip', 'rb') as f:
        lambda_zip = f.read()

    # Create or update lambda
    try:
        response = aws_lambda.create_function(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Runtime='python3.9',
            Role=role['Role']['Arn'],
            Handler='lambda_function.lambda_handler',
            Code=dict(ZipFile=lambda_zip),
            Timeout=300
        )
    except aws_lambda.exceptions.ResourceConflictException:
        response = aws_lambda.update_function_code(
            FunctionName=LAMBDA_FUNCTION_NAME,
            ZipFile=lambda_zip
        )


    #### Setup our step function ####
    print('Setting up state machine...')

    sfn = boto3.client('stepfunctions')

    lambda_arn = [f['FunctionArn'] 
                  for f in aws_lambda.list_functions()['Functions']
                  if f['FunctionName'] == LAMBDA_FUNCTION_NAME
                  ][0] 

    response = aws_lambda.put_function_concurrency(
        FunctionName=LAMBDA_FUNCTION_NAME,
        ReservedConcurrentExecutions=10
    )  

    sf_def = make_def(lambda_arn)

    try:
        response = sfn.create_state_machine(
            name=STEP_FUNCTION_NAME,
            definition=json.dumps(sf_def),
            roleArn=role['Role']['Arn'],
            type='EXPRESS'
        )
    except sfn.exceptions.StateMachineAlreadyExists:
        response = sfn.list_state_machines()
        state_machine_arn = [sm['stateMachineArn']
                             for sm in response['stateMachines']
                             if sm['name'] == STEP_FUNCTION_NAME][0]
        
        response = sfn.update_state_machine(
            stateMachineArn=state_machine_arn,
            definition=json.dumps(sf_def),
            roleArn=role['Role']['Arn']
        )
    
    #### Setup our bucket ####
    print('Setting up bucket...')

    bucket_client = boto3.client('s3')
    try:
        # bucket_client.create_bucket(ACL='public-read', 
        #                             Bucket=BUCKET,
        #                             GrantWriteACP=
        #                             ObjectOwnership='BucketOwnerPreferred')
        bucket_client.create_bucket(Bucket=BUCKET)
    except bucket_client.exceptions.BucketAlreadyExists:
        print('Bucket already exists, no further action needed.')

    print('Everything is setup!')