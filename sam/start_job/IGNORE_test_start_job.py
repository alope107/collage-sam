import boto3
from start_job import app


def test_request_job_returns_200_and_stores_input_data_in_s3(s3_put_event):
    app.lambda_handler(s3_put_event, "")

    batch_call = boto3.client("batch").put_object.call_args.kwargs
    assert batch_call["jobDefinition"] == "mock-job-definition"
    assert batch_call["jobQueue"] == "mock-job-queue"
    assert batch_call["jobName"] == "mock-object-key"
    assert batch_call["containerOverrides"] == {
        "command": ["mock-bucket-arn", "mock-object-id"]
    }
