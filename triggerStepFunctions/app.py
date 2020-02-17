import json
import boto3
import os
import io
import json
from zipfile import ZipFile

pipeline = boto3.client('codepipeline')
step_functions = boto3.client('stepfunctions')
s3_resource = boto3.resource('s3')
STATE_MACHINE_ARN = os.getenv('STATE_MACHINE_ARN')
SCENARIO_DEFINITIONS_FILENAME = os.getenv('SCENARIO_DEFINITIONS_FILENAME')

def lambda_handler(event, context):
    '''
    This lambda function is designed to be used in conjunction with CodePipeline. It can be set as an action in a CodePipline stage.
    This function will look for a JSON file (default, scenarios.json) and then 
    '''

    step_functions_response = ""
    code_pipeline_response = ""
    job_id = event['CodePipeline.job']['id']
    s3_location_obj = event['CodePipeline.job']['data']['inputArtifacts'][0]['location']['s3Location']
    
    ## Find the file defined in the env variable SCENARIO_DEFINITIONS_FILENAME and invoke the Step Functions state machine (STATE_MACHINE_ARN) with that JSON object.
    try:
        zip_obj = s3_resource.Object(bucket_name=s3_location_obj['bucketName'], key=s3_location_obj['objectKey'])
        buffer = io.BytesIO(zip_obj.get()["Body"].read())
        zipOut = ZipFile(buffer)
        
        for filename in zipOut.namelist():
            if (filename==SCENARIO_DEFINITIONS_FILENAME):
                filecontent = zipOut.open(filename)
                launch_json = json.loads(filecontent.read())
                launch_json['codePipelineJobId'] = job_id
        
        step_functions_response = step_functions.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps(launch_json)
        )
        
    except Exception as e:
        code_pipeline_response = pipeline.put_job_failure_result(jobId=job_id, failureDetails={
            'type': 'JobFailed',
            'message': str(e)
        })
        
    return {
        "statusCode": 200,
        "body": json.dumps({
            "step_functions_response": step_functions_response,
            "code_pipeline_response": code_pipeline_response
        }, indent=4, sort_keys=True, default=str),
    }