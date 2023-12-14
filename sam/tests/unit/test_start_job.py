import boto3
from start_job import app


def test_start_job_submits_a_job(s3_put_event):
    app.lambda_handler(s3_put_event, "")

    # batch_call = boto3.client("batch").submit_job.call_args.kwargs
    # assert batch_call["jobDefinition"] == "mock-job-definition"
    # assert batch_call["jobQueue"] == "mock-job-queue"
    # assert batch_call["jobName"] == "mock-id"
    # assert batch_call["containerOverrides"] == {
    #     "command": ["mock-bucket-name", "mock-id", "input/", "output/"]
    # }
