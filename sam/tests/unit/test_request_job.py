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
