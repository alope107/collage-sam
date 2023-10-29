import io
import os
from unittest.mock import Mock, patch

import pytest


def mock_boto3_client(config):
    '''
    Patches in a mock boto3 client and stores it in config._boto_patch
    Currently mocked services:
        - Secrets Manager
        - S3
    '''
    mock_secrets_client = Mock()
    mock_secrets_client.get_secret_value.return_value = {"SecretString": "my_secret_key"}

    mock_s3_client = Mock()

    clients = {
        "secretsmanager": mock_secrets_client,
        "s3": mock_s3_client
    }

    def get_client(service_name, *args, **kwargs):
        try:
            return clients[service_name]
        except KeyError:
            return Mock()

    patcher = patch('boto3.client')
    mock_boto_client = patcher.start()
    mock_boto_client.side_effect = get_client
    config._boto_patch = patcher


def mock_env_vars():
    os.environ["AWS_REGION"] = "mock-region"
    os.environ["INPUT_BUCKET"] = "mock-bucket"


def pytest_configure(config):
    mock_env_vars()
    mock_boto3_client(config)


def pytest_unconfigure(config):
    boto_patcher = getattr(config, '_boto_patch', None)
    if boto_patcher:
        boto_patcher.stop()


def create_multipart(fields, files):
    """
    Create multipart/form-data content with given fields and files.
    Adapted from: https://stackoverflow.com/questions/42786531/simulate-multipart-form-data-file-upload-with-falcons-testing-module

    :param fields: A dictionary of field names to values.
    :param files: A dictionary of field names to (filename, file_content, content_type) tuples.
    """
    boundary = '----WebKitFormBoundary1234567890123456'
    buff = io.BytesIO()

    # Add fields
    for key, value in fields.items():
        buff.write(b'--' + boundary.encode() + b'\r\n')
        buff.write(('Content-Disposition: form-data; name="%s"\r\n\r\n' % key).encode())
        buff.write(value.encode() + b'\r\n')

    # Add files
    for key, (filename, file_content, content_type) in files.items():
        buff.write(b'--' + boundary.encode() + b'\r\n')
        buff.write(('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename)).encode())
        buff.write(('Content-Type: %s\r\n\r\n' % content_type).encode())
        buff.write(file_content + b'\r\n')

    buff.write(b'--' + boundary.encode() + b'--\r\n')

    content = buff.getvalue()
    headers = {
        'Content-Type': 'multipart/form-data; boundary=%s' % boundary,
        'Content-Length': str(len(content))
    }

    return content, headers


@pytest.fixture
def api_gateway_event():
    """Fixture to generate a mock API Gateway event."""

    fields = {
        "token": "sample_token",
        "species": "human"
    }
    files = {
        "fasta": ("sample.fasta", b"mock-fasta-data", "application/octet-stream")
    }
    body, headers = create_multipart(fields, files)

    event = {
        "httpMethod": "POST",
        "isBase64Encoded": False,
        "headers": headers,
        "body": body
    }
    return event
