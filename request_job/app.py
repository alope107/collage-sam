import json
import requests
import os

SCORE_THRESH = .5


def get_recaptcha_secret() -> str:
    if os.getenv("AWS_SAM_LOCAL"):
        return os.environ["RECAPTCHA_SECRET"]
    else:
        raise NotImplementedError("Secret fetching not yet implemented")


RECAPTCHA_SECRET = get_recaptcha_secret()


def verify_recaptcha(secret_key: str, token: str, ip: str = None, thresh: float = SCORE_THRESH) -> bool:
    """Verify reCAPTCHA token with Google's reCAPTCHA API."""
    recaptcha_url = "https://www.google.com/recaptcha/api/siteverify"

    # Parameters for the API
    params = {
        "secret": secret_key,
        "response": token
    }
    if ip:
        params["remoteip"] = ip

    response = requests.post(recaptcha_url, params=params)
    result = response.json()

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
