import json
import boto3
import os

STATUS_BUCKET = os.environ.get("STATUS_BUCKET")
STATUS_PREFIX = "status/"
s3 = boto3.client('s3')


def lambda_handler(event, context):
    """
    Uploads status information to a JSON file in an S3 bucket when a batch job changes state.

    The bucket used is specified by the STATUS_BUCKET environment variable.
    The key for the S3 object is status/JOB_NAME.json
    The keys of the JSON object are jobName, status, and statusReason.

    Parameters
    ----------
    event: dict, required
        AWS Batch State Change Event

        Event doc: https://docs.aws.amazon.com/batch/latest/userguide/batch_cwe_events.html

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html
    """

    detail = event["detail"]

    job_info = {k: detail.get(k) for k in ("jobName", "status", "statusReason")}
    job_info_json = json.dumps(job_info).encode()

    print(job_info)

    key = f"{STATUS_PREFIX}{job_info['jobName']}.json"

    s3.put_object(
        Body=job_info_json,
        Bucket=STATUS_BUCKET,
        Key=key
    )
