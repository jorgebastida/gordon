import time
import json
import boto3
from botocore.exceptions import ClientError

from cfnresponse import send, SUCCESS, FAILED


def get_alias(function_name, alias_name):
    client = boto3.client('lambda')
    try:
        return client.get_alias(
            FunctionName=function_name,
            Name=alias_name
        )
    except ClientError, exc:
        if exc.response['Error']['Code'] == 'ResourceNotFoundException':
            return None
        raise


def create_alias(function_name, alias_name, function_version, description=''):
    client = boto3.client('lambda')
    return client.create_alias(
        FunctionName=function_name,
        Name=alias_name,
        FunctionVersion=function_version,
        Description=description
    )


def update_alias(function_name, alias_name, function_version, description=''):
    client = boto3.client('lambda')
    return client.update_alias(
        FunctionName=function_name,
        Name=alias_name,
        FunctionVersion=function_version,
        Description=description
    )

def handler(event, context):
    properties = event['ResourceProperties']
    alias = get_alias(properties['FunctionName'], properties['Name'])

    if event['RequestType'] == 'Delete':
        # We don't delete the alias, because the deletion of the fuction
        # will delete it on cascade, and because if an alias was created in
        # the past, and now the user don't want to re-point the alias on
        # deploy time, CF will try to delete the old alias, which is
        # totally not what we want to do.
        # if alias:
        #     client.delete_alias(
        #         FunctionName=properties['FunctionName'],
        #         Name=properties['Name']
        #     )
        send(event, context, SUCCESS)
        return

    # We don't check if RequestType is Create or Update, because we don't care
    # much... as regardless of what CF thinks the action is (and in order to
    # make this more resillient) we only need to know if the alias exists.
    if alias:
        action = update_alias
    else:
        action = create_alias

    output = action(
        properties['FunctionName'],
        properties['Name'],
        properties['FunctionVersion'],
        description=properties.get('Description', '')
    )

    send(event, context, SUCCESS, response_data={'Arn': output['AliasArn']})
