import boto3
import os
import re

session = boto3.session.Session()
batch_client = session.client('batch')
JOB_DEFINITION = os.environ.get("JOB_DEFINITION")
JOB_QUEUE = os.environ.get("JOB_QUEUE")

print(f"{JOB_DEFINITION=} {JOB_QUEUE=}")


def parse_job_name(object_key):
    return re.search(r"^input/(.+)$", object_key).group(1)


def lambda_handler(event, context):
    print(f"{JOB_DEFINITION=} {JOB_QUEUE=}")
    print(event)

    s3_info = event['Records'][0]['s3']
    bucket_arn = s3_info['bucket']['arn']
    object_key = s3_info['object']['key']

    cmd_args = [bucket_arn, object_key]

    job_name = parse_job_name(object_key)

    batch_client.submit_job(
        jobDefinition=JOB_DEFINITION,
        jobQueue=JOB_QUEUE,
        jobName=job_name,
        containerOverrides={
            "command": cmd_args
        }
    )
