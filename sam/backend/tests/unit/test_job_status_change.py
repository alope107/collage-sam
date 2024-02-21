import boto3
import json
from job_status_change.app import lambda_handler


def test_handler_extracts_details_without_reason():
    event = {
        "detail": {
            "jobName": "event-test-1",
            "status": "RUNNABLE",
        }
    }

    lambda_handler(event, "")

    s3_call = boto3.client('s3').put_object.call_args.kwargs
    assert s3_call["Bucket"] == 'mock-bucket'
    assert s3_call["Key"] == ('status/event-test-1.json')

    assert json.loads(s3_call["Body"]) == {
        "jobName": "event-test-1",
        "status": "RUNNABLE",
        "statusReason": None
    }


def test_handler_extracts_details_with_reason():
    event = {
        "detail": {
            "jobName": "event-test",
            "status": "FAILED",
            "statusReason": "OOM mate :("
        }
    }

    lambda_handler(event, "")

    s3_call = boto3.client('s3').put_object.call_args.kwargs
    assert s3_call["Bucket"] == 'mock-bucket'
    assert s3_call["Key"] == ('status/event-test.json')

    assert json.loads(s3_call["Body"]) == {
        "jobName": "event-test",
        "status": "FAILED",
        "statusReason": "OOM mate :("
    }
