import boto3
from app.job_runner import download_predict_upload
from unittest import mock


@mock.patch('app.job_runner.beam_generator')
@mock.patch('app.job_runner.initialize_collage_model')
@mock.patch('app.job_runner.parse_fasta')
def test_job_runner_gets_file_and_uploads_predictions_file_to_s3(mocked_parse, mocked_init, mocked_beam):
    # TODO(auberon): Don't mock parsing, and instead have s3 mock return actual fasta?
    mocked_parse.return_value = {"mock-sequence": "mock_sequence-data"}
    mocked_beam.return_value = {"TAGCAT": -42, "GAGAGA": -43}

    bucket = "mock-bucket"
    object_name = "mock-object-name"
    input_prefix = "mock-input-prefix/"
    output_prefix = "mock-output-prefix/"
    model_path = "/mock/path/to/model"
    beam_size = 100
    use_cpu = True

    download_predict_upload(bucket, object_name, input_prefix, output_prefix, model_path, beam_size, use_cpu)

    s3_client = boto3.client('s3')
    s3_get_call = s3_client.get_object.call_args.kwargs
    assert s3_get_call["Bucket"] == "mock-bucket"
    assert s3_get_call["Key"] == "mock-input-prefix/mock-object-name"

    s3_put_call = s3_client.put_object.call_args.kwargs
    assert s3_put_call["Bucket"] == "mock-bucket"
    assert s3_put_call["Key"] == "mock-output-prefix/mock-object-name"
    assert s3_put_call["Body"] == ">seq0: negLL: -42\nTAGCAT\n>seq1: negLL: -43\nGAGAGA\n"
