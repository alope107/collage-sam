import json
import uuid
import requests
import os
import boto3
import base64
import cgi
from requests_toolbelt.multipart import decoder

# Score above which to consider captcha passed
SCORE_THRESH = .5
RECAPTCHA_SECRET_ARN = os.getenv("RECAPTCHA_SECRET_ARN")
REGION = os.environ.get("AWS_REGION")
print(f"REGION: {REGION}")
RECAPTCHA_SECRET_NAME = "RecaptchaKeySecret"

INPUT_BUCKET = os.environ.get("INPUT_BUCKET")
INPUT_PREFIX = "input/"
print(f"INPUT_BUCKET: {INPUT_BUCKET}")

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


def decode_form_data(body: str, is_base64: bool, content_type: str) -> dict:
    if is_base64:
        body = base64.b64decode(body)

    multipart_data = decoder.MultipartDecoder(body, content_type)

    expected_parts = {"fasta": "file", "token": "string", "species": "string"}
    data = {}
    for part in multipart_data.parts:
        content_disposition = part.headers.get(b'Content-Disposition', b'').decode('utf-8')
        if content_disposition:
            parsed = cgi.parse_header(content_disposition)
            # TODO(auberon): More header validation?
            name = parsed[1]["name"]
            if name not in expected_parts:
                raise EarlyExitException(f"Malformed request, go unexpected form part '{name}'", 400)
            data[name] = part.text if expected_parts[name] == "text" else part.content
        else:
            raise EarlyExitException("Malformed request, missing Content-Disposition on form part", 400)

    for expected_part in expected_parts:
        if expected_part not in data:
            raise EarlyExitException(f"Malformed request, missing expected form part '{expected_part}'", 400)

    return data


def normalize_event_headers(event):
    """
    HTTP headers are case-insensitive. This normalizes them all to lower case.
    Taken from https://github.com/aws/aws-sam-cli/issues/1860
    """
    event["headers"].update(
        {name.lower(): value for name, value in event["headers"].items()}
    )


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

        normalize_event_headers(event)

        form_data = decode_form_data(event["body"], event["isBase64Encoded"], event["headers"]["content-type"])

        is_valid = verify_recaptcha(RECAPTCHA_SECRET, form_data["token"])

        s3_client = session.client(
            service_name="s3",
            region_name=REGION
        )

        input_id = uuid.uuid4().hex

        # TODO(auberon): Inspect response?
        s3_client.put_object(
            Body=form_data["fasta"],
            Bucket=INPUT_BUCKET,
            Key=f"{INPUT_PREFIX}{input_id}"
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"is_valid": is_valid, "id": input_id}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
            }
        }
    except EarlyExitException as e:
        return e.to_return
    except Exception as e:
        print(repr(e))
        return {
            "statusCode": 500,
            "body": json.dumps({
                "msg": "Internal error."
            })
        }
