import boto3
from app.job_runner import upload_download

def test_job_runner_gets_and_reuploads_file_to_s3():
    bucket = "mock-bucket"
    object_name = "mock-object-name"
    input_prefix = "mock-input-prefix/"
    output_prefix = "mock-output-prefix/"

    upload_download(bucket, object_name, input_prefix, output_prefix)

    s3_client = boto3.client('s3')
    s3_get_call = s3_client.get_object.call_args.kwargs
    assert s3_get_call["Bucket"] == "mock-bucket"
    assert s3_get_call["Key"] == "mock-input-prefix/mock-object-name"

    s3_put_call = s3_client.put_object.call_args.kwargs
    assert s3_put_call["Bucket"] == "mock-bucket"
    assert s3_put_call["Key"] == "mock-output-prefix/mock-object-name"
    # Skipping body validation for now as it will be different once the data is actually processed


