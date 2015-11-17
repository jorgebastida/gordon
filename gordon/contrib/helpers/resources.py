from gordon.utils import BaseLambdaAWSCustomObject


class Sleep(BaseLambdaAWSCustomObject):
    """CloudFormation Custom resource which waits ``Time`` seconds before
    succeeding."""

    resource_type = "Custom::Sleep"
    props = {
        'ServiceToken': (basestring, True),
        'Time': (int, True)
    }
