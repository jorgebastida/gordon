import time
import json
import boto3
from botocore.exceptions import ClientError

from cfnresponse import send, SUCCESS, FAILED


def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    client = boto3.client('apigateway')
    properties = event['ResourceProperties']
    physical_resource_id = properties.get('PhysicalResourceId')

    parent_id = properties['ParentId']
    api_id = properties['RestApiId']

    if parent_id == '/':
        for item in client.get_resources(restApiId=api_id).get('items', []):
            if item['path'] == '/':
                parent_id = item['id']

    if event['RequestType'] == 'Delete':
        client.delete_resource(
            restApiId=api_id,
            resourceId=physical_resource_id,
        )
        return send(event, context, SUCCESS)

    elif event['RequestType'] == 'Update':
        # client.update_rest_api(
        #     restApiId=physical_resource_id,
        #
        # )
        print "update"
    else:
        api = client.create_resource(
            restApiId=api_id,
            parentId=parent_id,
            pathPart=properties['PathPart']
        )
        physical_resource_id = api['id']

    send(event, context, SUCCESS, physical_resource_id=physical_resource_id)
