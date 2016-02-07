from gordon.utils import BaseLambdaAWSCustomObject
from troposphere import AWSProperty


class EventsRule(BaseLambdaAWSCustomObject):
    """
    CloudFormation Custom resource which creates a new CloudWatch events rule
    """

    resource_type = "Custom::EventsRule"
    props = {
        'ServiceToken': (basestring, True),
        'Name': (basestring, True),
        'RoleArn': (basestring, False),
        'ScheduleExpression': (basestring, False),
        'EventPattern': (basestring, False),
        'State': (basestring, True),
        'Description': (basestring, False),
    }

    def validate(self):
        required_any_properties = (
            'ScheduleExpression', 'EventPattern'
        )
        if not [p for p in self.properties if p in required_any_properties]:
            raise ValueError("""You need to specify any of {} in
            Custom::EventsRule""".format(
                ', '.join(required_any_properties))
            )


class Target(AWSProperty):
    props = {
        'Id': (basestring, True),
        'Arn': (basestring, True),
        'Input': (basestring, False),
        'InputPath': (basestring, False),
    }

    def validate(self):
        required_one_properties = (
            'Input', 'InputPath'
        )
        if len([p for p in self.properties if p in required_one_properties]) > 1:
            raise ValueError("""You need to specify one of {} in
            Custom::Target""".format(
                ', '.join(required_one_properties))
            )


class EventsTargets(BaseLambdaAWSCustomObject):

    resource_type = "Custom::EventsTargets"
    props = {
        'ServiceToken': (basestring, True),
        'Rule': (basestring, True),
        'Targets': ([Target], True),
    }
