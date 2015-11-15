import time
import json
import boto3

from cfnresponse import send, SUCCESS


def publish_version(function_name):
    print "Publishing version for {}".format(function_name)
    client = boto3.client('lambda')
    function = client.get_function(FunctionName=function_name)

    client.publish_version(
        FunctionName=function_name,
        CodeSha256=function['Configuration']['CodeSha256']
    )


def handler(event, context):
    if event['RequestType'] == 'Delete':
        send(event, context, SUCCESS)
        return

    publish_version(function_name=event['ResourceProperties']['FunctionName'])
    send(event, context, SUCCESS)
