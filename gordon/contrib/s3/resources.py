from gordon.utils import BaseLambdaAWSCustomObject
from troposphere import AWSProperty


def validate_key_filter_name(value):
    if value in ('prefix', 'suffix'):
        return value
    raise ValueError("Key Filter must be either prefix or suffix based.")


class KeyFilter(AWSProperty):
    props = {
        'Name': (validate_key_filter_name, True),
        'Value': (basestring, True),
    }


class NotificationConfiguration(AWSProperty):
    props = {
        'Id': (basestring, True),
        'DestinationArn': (basestring, True),
        'Events': ([basestring], True),
        'KeyFilters': ([KeyFilter], False),
    }


class S3BucketNotificationConfiguration(BaseLambdaAWSCustomObject):

    resource_type = "Custom::S3BucketNotificationConfiguration"

    props = {
        'ServiceToken': (basestring, True),
        'Bucket': (basestring, True),
        'TopicConfigurations': ([NotificationConfiguration], False),
        'QueueConfigurations': ([NotificationConfiguration], False),
        'LambdaFunctionConfigurations': ([NotificationConfiguration], False),
    }

    def validate(self):
        required_any_properties = (
            'TopicConfigurations', 'QueueConfigurations', 'LambdaFunctionConfigurations'
        )
        if not [p for p in self.properties if p in required_any_properties]:
            raise ValueError("""You need to specify any of {} in
            Custom::S3BucketNotificationConfiguration""".format(
                ', '.join(required_any_properties))
            )
