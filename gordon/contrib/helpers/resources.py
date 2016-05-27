import six

from gordon.utils import BaseLambdaAWSCustomObject


class Sleep(BaseLambdaAWSCustomObject):
    """CloudFormation Custom resource which waits ``Time`` seconds before
    succeeding."""

    resource_type = "Custom::Sleep"
    props = {
        'ServiceToken': (six.string_types, True),
        'Time': (int, True)
    }
