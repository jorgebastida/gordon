import json
import base64

import boto3
from snowplow_analytics_sdk import event_transformer, snowplow_event_transformation_exception


def handler(event, context):
    # Load gotrdon context
    with open('.context', 'r') as f:
        gordon_context = json.loads(f.read())
    
    print("Received event: " + json.dumps(event, indent=2))

    client = boto3.client('dynamodb')
    for record in event.get('Records', []):

        # Convert the raw event into a snowplow event
        raw_event = base64.b64decode(record['kinesis']['data'])
        try:
            snowplow_event = event_transformer.transform(raw_event)
        except snowplow_event_transformation_exception.SnowplowEventTransformationException as e:
            for error_message in e.error_messages:
                print(error_message)
            return "error!"

        # Update dynamodb with the new value for impressions
        response = client.update_item(
                TableName=gordon_context['dynamodb_table'],
                Key={
                    'message_id': {
                        'S': snowplow_event.get('se_label', '12345')
                    }
                },
                ReturnValues='ALL_NEW',
                ReturnConsumedCapacity='NONE',
                ReturnItemCollectionMetrics='NONE',
                UpdateExpression='ADD {} :val'.format(snowplow_event.get('se_category', 'impression')),
                ExpressionAttributeValues={
                    ':val': {
                        'N': snowplow_event.get('se_value', '1'),
                    }
                }
            )
        print response

    return "ok!"
