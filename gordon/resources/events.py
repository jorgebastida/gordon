import troposphere
from troposphere import events

from .base import BaseResource
from gordon import utils


class CloudWatchScheduledEvent(BaseResource):

    required_settings = (
        'schedule_expression',
        'lambda'
    )

    def get_enabled(self):
        """Returns if this stream is enable or not."""
        return ['DISABLED', 'ENABLED'][self._get_true_false('enabled')]

    def get_expression(self):
        """Returns a valid schedule expression"""
        return self.settings['schedule_expression']

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
        rule = events.Rule(
            utils.valid_cloudformation_name(self.name, "Rule"),
            Description=self.settings.get('description', ''),
            #EventPattern=,
            ScheduleExpression=self.get_expression(),
            State=self.get_enabled(),
            Targets=[
                events.Target(
                    Arn=self.get_destination_arn(),
                    Id=self.get_function_name(),
                )
            ]
        )
        template.add_resource(rule)

        template.add_resource(
            troposphere.awslambda.Permission(
                utils.valid_cloudformation_name(
                    self.name,
                    'rule',
                    'permission'
                ),
                Action="lambda:InvokeFunction",
                FunctionName=self.get_destination_arn(),
                Principal="events.amazonaws.com",
                SourceArn=troposphere.GetAtt(
                    rule, 'Arn'
                ),
            )
        )
