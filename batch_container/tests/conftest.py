from unittest.mock import Mock, patch

def mock_boto3_client(config):
    '''
    Patches in a mock boto3 client and stores it in config._boto_patch
    Currently mocked services:
        - S3
    '''
    mock_s3_client = Mock()
    mock_file = Mock()
    mock_file.read.return_value = "mock-file-data"
    mock_resp = {"Body": mock_file}
    mock_s3_client.get_object.return_value = mock_resp

    clients = {
        "s3": mock_s3_client,
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

def pytest_configure(config):
    mock_boto3_client(config)

def pytest_unconfigure(config):
    boto_patcher = getattr(config, '_boto_patch', None)
    if boto_patcher:
        boto_patcher.stop()