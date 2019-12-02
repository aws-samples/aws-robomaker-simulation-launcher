#
'''
    In this sample lambda function, multiple simulation jobs will be run based on a common configuration.
    
    Below is a sample event that you could use to invoke the lambda function and launch a set of simulations.
    
    {
        "wait": "5",
        "scenarios": {
            "": {
                "robotEnvironmentVariables": {}
                "simEnvironmentVariables": {}
            }
        },
        "simulations": [{
            "scenarios": ["<SCENARIO_NAME>"]
            "params": CreateSimulationJobParams
        }]
    }
    
'''

import json
import boto3
import time

client = boto3.client('robomaker')

def lambda_handler(event, context):
    responses = []
    numLaunchSuccess = 0
    totalJobs = 0
    
    print("Starting test simulations...")
    
    for simulation in event['simulations']:
        
        print("Running simulation %s..." % json.dumps(simulation))
        
        for x, scenario in enumerate(simulation['scenarios']):
            
            totalJobs += 1
            
            if scenario in event['scenarios'].keys():
                
                print("Scenario %s found..." % scenario)
                
                simulation['params']['tags'] = { "Scenario": scenario }
                y, z = 0, 0

                for y, robotApp in enumerate(simulation['params']['robotApplications']):
                    simulation['params']['robotApplications'][y]['launchConfig']['environmentVariables'] = event['scenarios'][scenario]['robotEnvironmentVariables']
                
                for z, simApp in enumerate(simulation['params']['simulationApplications']):
                    simulation['params']['simulationApplications'][z]['launchConfig']['environmentVariables'] = event['scenarios'][scenario]['simEnvironmentVariables']

                print("Running scenario %s..." % scenario)

                try:
                    print("Params %s: " % json.dumps(simulation['params']))
                    print("Starting simulation for scenario %s" % scenario)
                    # Create a new simulation job based on Lambda event data.
                    
                    response = client.create_simulation_job(**simulation['params'])
                                    
                    #For debugging
                    print(response)
                            
                    if (response):
                        numLaunchSuccess += 1
                        responses.append(response)
                    else:
                        raise Exception("No response.")
                except Exception as e:
                    print("Error runnning simulation, skipping. Error: %s ", e)
                finally:
                    # A defined wait period to not run into AWS API throttling issues.
                    # For more information on limits for AWS RoboMaker and other services, check out this link:
                    # https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html
                    if ((x+1)>=len(simulation['scenarios'])):
                        time.sleep(event['wait'])
            else:
                print("Scenario not found. Please check your JSON file.")
                
    return json.dumps({
        'statusCode': 200,
        'body': {
            'numLaunched': numLaunchSuccess,
            'numFailed': (totalJobs - numLaunchSuccess),
            'responses': responses
        }
    })
