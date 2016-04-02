from gordon.utils import BaseLambdaAWSCustomObject


class LambdaVersion(BaseLambdaAWSCustomObject):
    """
    CloudFormation Custom resource which registers a new version of a Lambda
    This resource doesn't use the ``S3ObjectVersion`` internally, but it is
    the nicest way to make CloudFormation trigger an UPDATE on it when the
    function code changes.
    """

    resource_type = "Custom::LambdaVersion"
    props = {
        'ServiceToken': (basestring, True),
        'FunctionName': (basestring, True),
        'S3ObjectVersion': (basestring, True)
    }
