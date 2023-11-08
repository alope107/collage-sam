import io
import sys
from unittest.mock import Mock, patch, MagicMock

# Attempt to import the module, and if it fails, create a mock.
# TODO(auberon): Look into less jank way to mock collage
# Challenge is that real collage may not be available at test time
# This challenge will be resolved once there is a pip installable version of collage
# Then it can just be mocked like any normal module
try:
    import collage
except ImportError:
    sys.modules['collage'] = MagicMock()

try:
    import collage.fasta
except ImportError:
    parse_fasta_result = {"mock-sequence": "mock_sequence-data"}
    fasta_module_mock = MagicMock()
    fasta_module_mock.parse_fasta.return_value = {"mock-sequence": "mock_sequence-data"}
    sys.modules['collage.fasta'] = fasta_module_mock

try:
    import collage.generator
except ImportError:
    sys.modules['collage.generator'] = MagicMock()

try:
    import collage.model
except ImportError:
    sys.modules['collage.model'] = MagicMock()

def mock_boto3_client(config):
    '''
    Patches in a mock boto3 client and stores it in config._boto_patch
    Currently mocked services:
        - S3
    '''
    mock_file_data = io.BytesIO(b"mock-file-data")
    mock_s3_client = Mock()
    mock_resp = {"Body": mock_file_data}
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