import boto3
from request_job import app
from unittest.mock import Mock, patch


@patch('request_job.app.verify_recaptcha', return_value=True)
def test_request_job_returns_200_and_stores_input_data_in_s3(recaptcha, api_gateway_event):
    ret = app.lambda_handler(api_gateway_event, "")
    assert ret["statusCode"] == 200

    s3_call = boto3.client('s3').put_object.call_args.kwargs
    assert s3_call["Body"] == b'mock-fasta-data'
    assert s3_call["Bucket"] == 'mock-bucket'
    assert s3_call["Key"].startswith('input/')

    # Cut off prefix to get object id
    object_id = s3_call["Key"][6:]

    batch_call = boto3.client("batch").submit_job.call_args.kwargs
    assert batch_call["jobDefinition"] == "mock-job-definition"
    assert batch_call["jobQueue"] == "mock-job-queue"
    assert batch_call["jobName"] == object_id
    assert batch_call["containerOverrides"] == {
        "command": ["mock-bucket", object_id, "input/", "output/", "--model_path", "/models/human.pt"]
    }
