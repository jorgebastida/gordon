import time
import json
import boto3

from cfnresponse import send, SUCCESS


def publish_version(function_name):
    client = boto3.client('lambda')
    function = client.get_function(FunctionName=function_name)

    return client.publish_version(
        FunctionName=function_name,
        CodeSha256=function['Configuration']['CodeSha256']
    )


def handler(event, context, sleep=5):
    if event['RequestType'] == 'Delete':
        send(event, context, SUCCESS)
        return

    output = publish_version(function_name=event['ResourceProperties']['FunctionName'])

    # Wait a bit until the version becomes available.
    # FUTURE: Loop until available
    time.sleep(sleep)

    send(event, context, SUCCESS,
        response_data={'Version': output['Version']}
    )
