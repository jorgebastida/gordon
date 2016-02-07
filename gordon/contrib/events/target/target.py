import boto3

from cfnresponse import send, SUCCESS


def create_or_update_target(rule_name, targets=None):
    client = boto3.client('events')
    targets = targets or []
    return client.put_targets(
        Rule=rule_name,
        Targets=targets or []
    )


def delete_targets(rule_name):
    client = boto3.client('events')
    return client.remove_targets(
        Rule=rule_name,
        Ids=[r['Id'] for r in client.list_targets_by_rule(Rule=rule_name)['Targets']]
    )


def handler(event, context):
    properties = event['ResourceProperties']
    physical_resource_id = 'rule-targets-{}'.format(properties['Rule'])

    if event['RequestType'] == 'Delete':
        delete_targets(properties['Rule'])
        send(event, context, SUCCESS)
        return

    create_or_update_target(
        rule_name=properties['Rule'],
        targets=properties.get('Targets', []),
    )

    send(event, context, SUCCESS, physical_resource_id=physical_resource_id)
