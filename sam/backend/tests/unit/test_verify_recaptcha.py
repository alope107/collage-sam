import pytest
from unittest.mock import Mock, patch
from request_job.app import verify_recaptcha, EarlyExitException, RECAPTCHA_URL, SCORE_THRESH


@patch('requests.post')
def test_verify_recaptcha_success(mock_post):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "score": SCORE_THRESH + 0.1  # Greater than the threshold
    }
    mock_post.return_value = mock_response
    secret_key = "my_secret_key"
    token = "my_token"
    ip = "my_ip"

    # Act
    result = verify_recaptcha(secret_key, token, ip)

    # Assert
    mock_post.assert_called_once_with(RECAPTCHA_URL, params={
        "secret": secret_key,
        "response": token,
        "remoteip": ip,
    })
    assert result is True


@patch('requests.post')
def test_verify_recaptcha_fail_invalid_score(mock_post):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "score": SCORE_THRESH - 0.1  # Less than the threshold
    }
    mock_post.return_value = mock_response
    secret_key = "my_secret_key"
    token = "my_token"

    # Act
    result = verify_recaptcha(secret_key, token)

    # Assert
    mock_post.assert_called_once_with(RECAPTCHA_URL, params={
        "secret": secret_key,
        "response": token,
    })
    assert result is False


@patch('requests.post')
def test_verify_recaptcha_fail_no_success(mock_post):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "score": SCORE_THRESH + 0.1  # Greater than the threshold, but no success
    }
    mock_post.return_value = mock_response
    secret_key = "my_secret_key"
    token = "my_token"

    # Act
    result = verify_recaptcha(secret_key, token)

    # Assert
    mock_post.assert_called_once_with(RECAPTCHA_URL, params={
        "secret": secret_key,
        "response": token,
    })
    assert result is False


@patch('requests.post')
def test_verify_recaptcha_fail_status_code(mock_post):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.json.return_value = {}  # Doesn't matter what's in here for this test
    mock_post.return_value = mock_response
    secret_key = "my_secret_key"
    token = "my_token"

    # Act and Assert
    with pytest.raises(EarlyExitException):
        verify_recaptcha(secret_key, token)


@patch('requests.post')
def test_verify_recaptcha_fail_no_json(mock_post):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError()  # Simulate a JSON decoding error
    mock_post.return_value = mock_response
    secret_key = "my_secret_key"
    token = "my_token"

    # Act and Assert
    with pytest.raises(EarlyExitException):
        verify_recaptcha(secret_key, token)
