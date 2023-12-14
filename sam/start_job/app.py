import boto3
import os
import re

batch_client = boto3.client('batch')
JOB_DEFINITION = os.environ.get("JOB_DEFINITION")
JOB_QUEUE = os.environ.get("JOB_QUEUE")
INPUT_PREFIX = "input/"
OUTPUT_PREFIX = "output/"

print(f"{JOB_DEFINITION=} {JOB_QUEUE=}")


def parse_object_name(object_key):
    return re.search(f"^{INPUT_PREFIX}(.+)$", object_key).group(1)


def lambda_handler(event, context):
    print(f"{JOB_DEFINITION=} {JOB_QUEUE=}")
    print(event)

    s3_info = event['Records'][0]['s3']
    bucket_name = s3_info['bucket']['name']
    object_key = s3_info['object']['key']

    object_name = parse_object_name(object_key)

    cmd_args = [bucket_name, object_name, INPUT_PREFIX, OUTPUT_PREFIX]

    print("SKIPPING SUBMIT, HOPEFULLY THIS FUNCTION IS OBSOLETE")
    # batch_client.submit_job(
    #     jobDefinition=JOB_DEFINITION,
    #     jobQueue=JOB_QUEUE,
    #     jobName=object_name,
    #     containerOverrides={
    #         "command": cmd_args
    #     }
    # )
