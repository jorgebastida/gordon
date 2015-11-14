from troposphere import cloudformation, Join, Ref
from gordon.utils import valid_cloudformation_name, BaseLambdaAWSCustomObject


class Sleep(BaseLambdaAWSCustomObject):
    """CloudFormation Custom resource which waits ``Time`` seconds before
    succeeding."""

    resource_type = "Custom::Sleep"
    props = {
        'ServiceToken': (basestring, True),
        'Time': (int, True)
    }
