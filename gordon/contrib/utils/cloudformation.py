from troposphere import cloudformation, Join, Ref
from gordon.utils import valid_cloudformation_name, BaseLambdaAWSCustomObject


class Sleep(BaseLambdaAWSCustomObject):
    """CloudFormation Custom resource which waits ``Time`` seconds before
    succeeding."""

    resource_type = "Custom::Sleep"
    lambda_name = 'gordon_contrib_utils_sleep'

    props = {
        'ServiceToken': (basestring, True),
        'Time': (int, True)
    }
