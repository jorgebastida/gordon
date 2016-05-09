import troposphere
from troposphere import events

from .base import BaseResource
from gordon import utils


class CloudWatchScheduledEvent(BaseResource):

    required_settings = (
        'expression',
        'lambda'
    )

    def get_enabled(self):
        """Returns if this stream is enable or not."""
        return ['DISABLED', 'ENABLED'][self._get_true_false('enabled')]

    def get_expression(self):
        """Returns a valid schedule expression"""
        return self.settings['expression']

    def get_function_name(self):
        """Returns a reference to the current alias of the lambda which will
        process this stream."""
        return self.project.reference(
            utils.lambda_friendly_name_to_grn(
                self.settings.get('lambda')
            )
        )

    def get_destination_arn(self):
        return troposphere.Ref(
            self.get_function_name()
        )

    def register_resources_template(self, template):
        role = troposphere.iam.Role(
            utils.valid_cloudformation_name(self.name, 'Role'),
            AssumeRolePolicyDocument={
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {
                        "Service": ["events.amazonaws.com"]
                    },
                    "Action": ["sts:AssumeRole"]
                }]
            },
            Policies=[
                troposphere.iam.Policy(
                    PolicyName=utils.valid_cloudformation_name(self.name, 'Policy'),
                    PolicyDocument={
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "lambda:InvokeFunction"
                                ],
                                "Resource": [
                                    "*"
                                ]
                            }
                        ]
                    }
                )
            ]
        )
        template.add_resource(role)

        rule_resource_name = utils.valid_cloudformation_name(self.name, "Rule")
        rule_name = troposphere.Join(
            "-",
            [troposphere.Ref(troposphere.AWS_STACK_NAME), rule_resource_name]
        )
        rule = events.Rule(
            rule_resource_name,
            Description=self.settings.get('description', ''),
            #EventPattern=,
            Name=rule_name,
            RoleArn=troposphere.GetAtt(role, 'Arn'),
            ScheduleExpression=self.get_expression(),
            State=self.get_enabled(),
            Targets=[
                events.Target(
                    Arn=self.get_destination_arn(),
                    Id=self.get_function_name(),
                    # Input=,
                    # InputPath=,
                )
            ]
        )
        template.add_resource(rule)
