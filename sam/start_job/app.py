import boto3
import os

session = boto3.session.Session()
batch_client = session.client('batch')
JOB_DEFINITION = os.environ.get("JOB_DEFINITION")
JOB_QUEUE = os.environ.get("JOB_QUEUE")

print(f"{JOB_DEFINITION=} {JOB_QUEUE=}")


def lambda_handler(event, context):
    print(f"{JOB_DEFINITION=} {JOB_QUEUE=}")
    print(event)

    # TODO(auberon): Fetch this from the event
    cmd_args = ["hello", "world"]

    batch_client.submit_job(
        jobDefinition=JOB_DEFINITION,
        jobQueue=JOB_QUEUE,
        jobName="dummy",  # TODO(auberon): Later get this from the event
        containerOverrides={
            "command": cmd_args
        }
    )
