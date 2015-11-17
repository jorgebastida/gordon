import time
import json
import boto3
from botocore.exceptions import ClientError

from cfnresponse import send, SUCCESS, FAILED


def handler(event, context):
    properties = event['ResourceProperties']

    if event['RequestType'] == 'Delete':
        send(event, context, SUCCESS)
        return

    send(event, context, SUCCESS)
