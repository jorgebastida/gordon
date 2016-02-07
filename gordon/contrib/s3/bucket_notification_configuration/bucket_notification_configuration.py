import boto3

from cfnresponse import send, SUCCESS, FAILED

AVAILABLE_CONFIGURATIONS = (
    'LambdaFunctionConfigurations',
    'TopicConfigurations',
    'QueueConfigurations'
)


def handler(event, context):
    """
    Bucket notifications configuration has a disgraceful API - sorry.
    The problem is that you can't individually deal with each configuration
    and you need to send a (potentially) enormous dictionary with all the
    configuration. This has lot's of implications when you are trying to
    implement a tool like gordon:
      - People might have already some notifications configured.
      - People might change them - which causes race conditions.
    The approach we have decided to follow is the following:
    1) If there is no configuration attached to this bucket, we continue.
    2) If there is any configuration attached, we check that the ID of
       each notification starts with "gordon-". If that's the case, we are
       "safe"... in the sense that whatever is the previous status we
       have the new "correct" configuration.
       If there is any notification with an id which doesn't starts with
       "gordon-" we fail miserably... because it is quite risky to start
       mixing events between two sources.
       We need to make this behaviour pretty clear in the documentation.

    Why the physical_resource_id is constant accross notification configurations
    of the same bucket is a workaround the same issue. We need to keep it
    constant so CloudFormation don't issue a delete on the old resource once
    the old one gets updated and get a new physical_resource_id because
    (for example) the lambda ID has changed. As result, CF will only trigger
    a delete when the bucket changes - which is expected.
    """
    properties = event['ResourceProperties']

    # It doesn't matter how big you put this on the doc... people wil
    # always put bucket's arn instead of name... and it would be a shame
    # to fail because this stupid error.
    buckent_name = properties['Bucket'].replace('arn:aws:s3:::', '')
    physical_resource_id = '{}-bucket-notification-configuration'.format(buckent_name)

    client = boto3.client('s3')
    existing_notifications = client.get_bucket_notification_configuration(
        Bucket=buckent_name
    )

    # Check if there is any notification-id which doesn't start with gordon-
    # If so... fail.
    for _type in AVAILABLE_CONFIGURATIONS:
        for notification in existing_notifications.get(_type, []):
            if not notification.get('Id', '').startswith('gordon-'):
                send(
                    event,
                    context,
                    FAILED,
                    physical_resource_id=physical_resource_id,
                    reason=("Bucket {} contains a notification called {} "
                            "which was not created by gordon, hence the risk "
                            "of trying it to add/modify/delete new notifications. "
                            "Please check the documentation in order to understand "
                            "why gordon refuses to proceed.").format(
                                buckent_name,
                                notification.get('Id', '')
                     )
                )
                return

    # For Delete requests, we need to simply send an empty dictionary.
    # Again - this have bad implications if the user has tried to configure
    # notification manually, because we are going to override their
    # configuration. There is no much else we can do.
    configuration = {}
    if event['RequestType'] != 'Delete':

        arn_name_map = {
            'LambdaFunctionConfigurations': 'LambdaFunctionArn',
            'TopicConfigurations': 'TopicArn',
            'QueueConfigurations': 'QueueArn',
        }

        for _type in AVAILABLE_CONFIGURATIONS:
            configuration[_type] = []
            for notification in properties.get(_type, []):
                data = {
                    'Id': notification['Id'],
                    arn_name_map.get(_type): notification['DestinationArn'],
                    'Events': notification['Events'],
                }
                if notification['KeyFilters']:
                    data['Filter'] = {
                        'Key': {
                            'FilterRules': notification['KeyFilters']
                        }
                    }
                configuration[_type].append(data)

    client.put_bucket_notification_configuration(
        Bucket=buckent_name,
        NotificationConfiguration=configuration
    )

    send(event, context, SUCCESS, physical_resource_id=physical_resource_id)
