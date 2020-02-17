import json
import boto3

pipeline = boto3.client('codepipeline')
        
def lambda_handler(event, context):
    '''
    This lambda function catches any errors in the simulation launching and monitoring workflow. If it fails, we return a fail to CodePipeline with a message that summarizes the error.
    {
        'codePipelineJobId': 'The CodePipeline ID',
        'error': {
                'Cause': 'The cause of the error.'
        }
    }
    '''    
    code_pipeline_response = pipeline.put_job_failure_result(jobId=event['codePipelineJobId'], failureDetails={
            'type': 'JobFailed',
            'message': event['error']['Cause']
    })
        
    return 'Simulations failed.'