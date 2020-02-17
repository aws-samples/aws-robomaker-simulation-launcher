import json
import boto3

client = boto3.client('robomaker')

def lambda_handler(event, context):
    '''
    This lambda function will check the status of a batch job and return the status along with an array of ARNs of the successful simulation jobs once complete.
    It is used with the aws-robomaker-simulation-launcher StepFunctions state machine.
    
    Event Structure:
    { 
        arns: Array | Completed individual simulation job ARNs. 
        isDone: Boolean | if the batch simulation describe call returns complete.
        batchSimJobArn: String | The ARN of the simulation batch.
        status: String | InProgress, Success or Failed for downstream processing.
        codePipelineJobId: String | The ID of the active CodePipeline job.
    }

    '''

    # If no batchSimJobArn is set, there was an error with a previous step.
    if (event['batchSimJobArn']):  
        
        # Set the default output. 
        output = { 'arns': None, 'isDone': False, 'batchSimJobArn': event['batchSimJobArn'], 'status': 'InProgress', 'codePipelineJobId': event['codePipelineJobId']}
        arns = []

        response = client.describe_simulation_job_batch(
            batch = event['batchSimJobArn']
        )
        
        if response['status'] == 'Completed':

            output['isDone'] = True
            
            # In this sample, we fail the code pipeline on any test failure. 
            if len(response['failedRequests']) == 0:
                output['status'] = 'Success'
            else:
                output['status'] = 'Failed'
                
            for job_output in response['createdRequests']:
                arns.append(job_output['arn'])
            
            output['arns'] = arns
            
        elif response['status'] == 'Failed' or response['status'] == 'Canceled':
            output['isDone'] = True
            output['status'] = 'Failed'
 
    else:
        output['isDone'] = True
        output['status'] = 'Failed'

    return output