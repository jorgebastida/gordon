from gordon.utils import BaseLambdaAWSCustomObject


class APIGatewayRestAPI(BaseLambdaAWSCustomObject):
    """CloudFormation Custom resource which manages API Gateway REST Resources"""

    resource_type = "Custom::APIGatewayRestAPI"
    props = {
        'ServiceToken': (basestring, True),
        'Name': (basestring, True),
        'Description': (basestring, True),
    }


class APIGatewayResource(BaseLambdaAWSCustomObject):
    """CloudFormation Custom resource which manages a Resource"""

    resource_type = "Custom::APIGatewayResource"
    props = {
        'ServiceToken': (basestring, True),
        'RestApiId': (basestring, True),
        'ParentId': (basestring, True),
        'PathPart': (basestring, True),
    }
