import time
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

    # We don't want to delete versions when CloudFormation says so, because
    # we want to keep them forever. If this delete comes from a stack delete
    # operation, deleteing the lambda will delete all related versions.
    if event['RequestType'] == 'Delete':
        send(event, context, SUCCESS)
        return

    output = publish_version(function_name=event['ResourceProperties']['FunctionName'])

    # Wait a bit until the version becomes available.
    # FUTURE: Loop until available
    time.sleep(sleep)

    send(event, context, SUCCESS, response_data={'Version': output['Version']})
