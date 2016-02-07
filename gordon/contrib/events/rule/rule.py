import boto3

from cfnresponse import send, SUCCESS


def create_or_update_rule(rule_name, role_arn='', schedule_expression='',
                          event_pattern='', state='ENABLED', description=''):
    client = boto3.client('events')
    extra = {}
    if schedule_expression:
        extra['ScheduleExpression'] = schedule_expression
    if event_pattern:
        extra['EventPattern'] = event_pattern
    if role_arn:
        extra['RoleArn'] = role_arn
    return client.put_rule(
        Name=rule_name,
        State=state,
        Description=description,
        **extra
    )


def delete_rule(rule_name):
    client = boto3.client('events')
    return client.delete_rule(
        Name=rule_name
    )


def handler(event, context):
    properties = event['ResourceProperties']
    rule_name = properties['Name'][:64]  # Rule Names can't be longer than 64 characters.
    physical_resource_id = 'rule-{}'.format(rule_name)

    if event['RequestType'] == 'Delete':
        delete_rule(rule_name)
        send(event, context, SUCCESS)
        return

    # We don't check if RequestType is Create or Update, because we don't care
    # much... as regardless of what CF thinks.
    output = create_or_update_rule(
        rule_name=rule_name,
        role_arn=properties.get('RoleArn', ''),
        schedule_expression=properties.get('ScheduleExpression', ''),
        event_pattern=properties.get('EventPattern', ''),
        state=properties.get('State', 'ENABLED'),
        description=properties.get('Description', '')
    )

    send(event, context, SUCCESS, physical_resource_id=physical_resource_id, response_data={'Arn': output['RuleArn']})
