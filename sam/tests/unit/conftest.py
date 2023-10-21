import os
from unittest.mock import Mock, patch


def mock_boto3_client(config):
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
    os.environ["AWS_REGION"] = "us-west-1"


def pytest_configure(config):
    mock_env_vars()
    mock_boto3_client(config)


def pytest_unconfigure(config):
    boto_patcher = getattr(config, '_boto_patch', None)
    if boto_patcher:
        boto_patcher.stop()
