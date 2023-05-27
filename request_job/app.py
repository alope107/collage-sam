import json
import requests
import os
import boto3

# Score above which to consider captcha passed
SCORE_THRESH = .5
RECAPTCHA_SECRET_ARN = os.getenv("RECAPTCHA_SECRET_ARN")
REGION = "us-east-1"  # TODO(auberon): Get this programatically?
RECAPTCHA_SECRET_NAME = "RecaptchaKeySecret"

session = boto3.session.Session()


def get_recaptcha_secret() -> str:
    '''
    Fetches the recaptcha service secret key.
    Fetches from RECAPTCHA_SECRET enviornment variable when using sam local.
    TODO(auberon): Fetch from AWS secrets when depoyed.
    '''
    if not RECAPTCHA_SECRET_ARN:
        print("Could not find secret ARN, falling back to environment variable")
        return os.environ["RECAPTCHA_SECRET"]

    secrets_client = session.client(
        service_name="secretsmanager",
        region_name=REGION
    )

    # If this fails we do want the entire lambda to fail so we won't try to catch
    # This will cause the gateway to return a 5XX error code
    secret_response = secrets_client.get_secret_value(SecretId=RECAPTCHA_SECRET_NAME)
    return secret_response["SecretString"]


RECAPTCHA_SECRET = get_recaptcha_secret()
RECAPTCHA_URL = "https://www.google.com/recaptcha/api/siteverify"


class EarlyExitException(Exception):
    '''
    Utility class similar to Flask's `abort` functionality.
    Meant to be caught at the top level handler.
    If caught, the top level handler should return to_return.
    '''

    def __init__(self, message: str, status_code: int):
        self.to_return = {
            "statusCode": status_code,
            "body": json.dumps({
                "msg": message
            })
        }


def verify_recaptcha(secret_key: str, token: str, ip: str = None, thresh: float = SCORE_THRESH) -> bool:
    """Verify reCAPTCHA token with Google's reCAPTCHA API."""
    params = {
        "secret": secret_key,
        "response": token
    }
    if ip:
        params["remoteip"] = ip

    # TODO(auberon) Remove this once secret fetching is working
    if not os.getenv("AWS_SAM_LOCAL") and not RECAPTCHA_URL:
        print("TEMPORARILY BYPASSING CAPTCHA VALIDATION")
        return True

    response = requests.post(RECAPTCHA_URL, params=params)

    if response.status_code != 200:
        # TODO(auberon): Retry on 429, others?
        raise EarlyExitException("Internal error when trying to resolve captcha", 500)
    try:
        result = response.json()
    except ValueError:
        raise EarlyExitException("Internal error when trying to resolve captcha", 500)

    return result.get("success", False) and result.get("score", False) >= thresh


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    try:
        if event['httpMethod'] == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
                },
                'body': ''
            }

        request_body = json.loads(event["body"])

        if "token" not in request_body:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "msg": "Missing required element of request body: token"
                })
            }

        is_valid = verify_recaptcha(RECAPTCHA_SECRET, request_body["token"])

        return {
            "statusCode": 200,
            "body": json.dumps({"is_valid": is_valid}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
            }
        }
    except EarlyExitException as e:
        return e.to_return
    except:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "msg": "Internal error."
            })
        }
