import time
import json
import boto3
from botocore.exceptions import ClientError

from cfnresponse import send, SUCCESS, FAILED


def get_rule(rule_name):
    client = boto3.client('events')
    try:
        return client.describe_rule(
            Name=rule_name
        )
    except ClientError, exc:
        if exc.response['Error']['Code'] == 'ResourceNotFoundException':
            return None
        raise


def create_or_update_rule(rule_name, role_arn='', schedule_expression='', event_pattern='', state='ENABLED', description=''):
    client = boto3.client('events')
    return client.put_rule(
        Name=rule_name,
        State=state,
        ScheduleExpression=schedule_expression,
        EventPattern=event_pattern,
        Description=description,
        RoleArn=role_arn
    )

def delete_rule(rule_name):
    client = boto3.client('events')
    return client.delete_rule(
        Name=rule_name
    )


def handler(event, context):
    properties = event['ResourceProperties']
    rule = get_rule(properties['RuleName'])

    if event['RequestType'] == 'Delete':
        delete_rule(properties['RuleName'])
        send(event, context, SUCCESS)
        return

    # We don't check if RequestType is Create or Update, because we don't care
    # much... as regardless of what CF thinks.
    output = create_or_update_rule(
        rule_name=properties['RuleName'],
        role_arn=properties.get('RoleArn', ''),
        schedule_expression=properties.get('ScheduleExpression', ''),
        event_pattern=properties.get('EventPattern', ''),
        state=properties.get('State', 'ENABLED'),
        description=properties.get('Description', '')
    )

    send(event, context, SUCCESS, response_data={'Arn': output['RuleArn']})
