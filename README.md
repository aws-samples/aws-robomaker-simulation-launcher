# Batch Simulations with Custom Scenarios
### Version 0.0.1

This function will create a set of AWS RoboMaker simulation jobs based on scenario criteria defined.

- batch_simulations - Main python script that will run the simulations.
- events - A sample set of scenarios, and an example of the JSON structure to use with the Lambda function.
- template.yaml - The template that creates the resources you would need.

## Event Structure

Here is the event structure (what to send to the lambda function when you invoke it):

```json
    {
        "wait": "5",
        "scenarios": {
            "": {
                "robotEnvironmentVariables": {},
                "simEnvironmentVariables": {}
            }
        },
        "simulations": [{
            "scenarios": ["<SCENARIO_NAME>"],
            "params": CreateSimulationJobParams
        }]
    }
```

A **scenario** is created by defining a set of environment variables, a set for the robot and simulation applications defined. The collection of environment variables can be referenced when configuring the simulations jobs that you want to run in parallel. 

**Example Scenario:**
```json
...
      "scenarios": {
        "BasicSlowTest": {
            "robotEnvironmentVariables": {
                "TIME_TEST_LENGTH_IN_SECONDS": "60",
                "SPEED_IN_RADIANS_PER_SECOND": "0.2"
            },
            "simEnvironmentVariables": {}
        }
      }
...
```

Once you have defined a set of scenarios (or more simply, your groups of environment variables) you can associate a scenario with a simulation job. Each scenario, simulation pair will result in a single AWS RoboMaker CreateSimulation API call. For example, the below configuration will create **two** AWS RoboMaker simulation jobs. One for each of the scenarios (BasicSlowTest and LongFastTest). The **params** field expects the same request syntax as what the [create_simulation_job](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/robomaker.html#RoboMaker.Client.create_simulation_job) method expects, which is simply the parameters for your simulation job assets. 

```json
...
    "simulations": [{
        "scenarios": ["BasicSlowTest","LongFastTest"],
        "params": {
               "failureBehavior": "Fail",
               "iamRole": "string",
               "maxJobDurationInSeconds": 600,
               "outputLocation": { 
                  "s3Bucket": "<S3_BUCKET_NAME>",
                  "s3Prefix": "logs"
               },
               "robotApplications": [ 
                  { 
                     "application": "<ROBOT_APPLICATION_ARN>",
                     "applicationVersion": "1",
                     "launchConfig": { 
                        "launchFile": "rotate.launch",
                        "packageName": "hello_world_robot"
                     }
                  }
               ],
               "simulationApplications": [ 
                  { 
                     "application": "<SIMULATION_APPLICATION_ARN>",
                     "applicationVersion": "1",
                     "launchConfig": { 
                        "launchFile": "empty_world.launch",
                        "packageName": "hello_world_simulation"
                     }
                  }
               ]
        }
    }]
...
```

## Deploy the sample application

This application has been built using the Serverless Application Model. 

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

* AWS CLI - [Install the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) and [configure it with your AWS credentials].
* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3 installed](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

The SAM CLI uses an Amazon S3 bucket to store your application's deployment artifacts. If you don't have a bucket suitable for this purpose, create one. Replace `BUCKET_NAME` in the commands in this section with a unique bucket name.

```bash
batch-simulations-scenarios$ aws s3 mb s3://BUCKET_NAME
```

To prepare the application for deployment, use the `sam build` and `sam package` command.

```bash
batch-simulations-scenarios$ sam build
batch-simulations-scenarios$ sam package \
    --output-template-file packaged.yaml \
    --s3-bucket BUCKET_NAME
```

The SAM CLI creates deployment packages, uploads them to the S3 bucket, and creates a new version of the template that refers to the artifacts in the bucket. 

To deploy the application, use the `sam deploy` command.

```bash
batch-simulations-scenarios$ sam deploy \
    --template-file packaged.yaml \
    --stack-name batch-simulations-scenarios \
    --capabilities CAPABILITY_IAM
```

After deployment is complete you can run the following command to retrieve the API Gateway Endpoint URL:

```bash
batch-simulations-scenarios$ aws cloudformation describe-stacks \
    --stack-name batch-simulations-scenarios \
    --query 'Stacks[].Outputs[?OutputKey==`HelloWorldApi`]' \
    --output table
``` 

## Use the SAM CLI to build and test locally

Build your application with the `sam build` command.

```bash
batch-simulations-scenarios$ sam build
```

The SAM CLI installs dependencies defined in `batch_simulations/requirements.txt`, creates a deployment package, and saves it in the `.aws-sam/build` folder.

Test a single function by invoking it directly with a test event. An event is a JSON document that represents the input that the function receives from the event source. Test events are included in the `events` folder in this project.

Run functions locally and invoke them with the `sam local invoke` command.

```bash
batch-simulations-scenarios$ sam local invoke batchsimulations --event events/event.json
```

## Add a resource to your application
The application template uses AWS Serverless Application Model (AWS SAM) to define application resources. AWS SAM is an extension of AWS CloudFormation with a simpler syntax for configuring common serverless application resources such as functions, triggers, and APIs. For resources not included in [the SAM specification](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md), you can use standard [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html) resource types.

## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
batch-simulations-scenarios$ sam logs -n HelloWorldFunction --stack-name batch-simulations-scenarios --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Cleanup

To delete the sample application and the bucket that you created, use the AWS CLI.

```bash
batch-simulations-scenarios$ aws cloudformation delete-stack --stack-name batch-simulations-scenarios
batch-simulations-scenarios$ aws s3 rb s3://BUCKET_NAME
```
## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)
