import time
import json
import boto3
from botocore.exceptions import ClientError

from cfnresponse import send, SUCCESS, FAILED

def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    properties = event['ResourceProperties']
    physical_resource_id = properties.get('PhysicalResourceId')
    client = boto3.client('apigateway')


    if event['RequestType'] == 'Delete':
        client.delete_rest_api(
            restApiId=physical_resource_id,

        )
        return send(event, context, SUCCESS)

    elif event['RequestType'] == 'Update':
        # client.update_rest_api(
        #     restApiId=physical_resource_id,
        #
        # )
        print "update"
    else:
        api = client.create_rest_api(
            name=properties['Name'],
            description=properties.get('Description', ''),
        )
        physical_resource_id = api['id']

    send(event, context, SUCCESS, physical_resource_id=physical_resource_id, response_data={'Id': physical_resource_id})
