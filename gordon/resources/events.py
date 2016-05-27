import six
import troposphere
from troposphere import events

from .base import BaseResource
from gordon import utils


class CloudWatchEvent(BaseResource):

    def get_enabled(self):
        """Returns if this stream is enable or not."""
        return ['DISABLED', 'ENABLED'][self._get_true_false('enabled')]

    def get_function_name(self, name):
        """Returns a reference to the current alias of the lambda which will
        process this stream."""
        return self.project.reference(
            utils.lambda_friendly_name_to_grn(
                name
            )
        )

    def get_destination_arn(self, name):
        return troposphere.Ref(
            self.get_function_name(name)
        )

    def register_resources_template(self, template):
        targets, target_lambdas = [], []
        for name, target in six.iteritems(self.settings.get('targets', {})):
            target_lambdas.append(target['lambda'])
            targets.append(
                events.Target(
                    Arn=self.get_destination_arn(target['lambda']),
                    Id=self.get_function_name(target['lambda']),
                    Input=target.get('input', ''),
                    InputPath=target.get('input_path', ''),
                )
            )

        rule = events.Rule(
            utils.valid_cloudformation_name(self.name, "Rule"),
            Description=self.settings.get('description', ''),
            EventPattern=self.settings.get('event_pattern', troposphere.Ref(troposphere.AWS_NO_VALUE)),
            ScheduleExpression=self.settings.get('schedule_expression', troposphere.Ref(troposphere.AWS_NO_VALUE)),
            State=self.get_enabled(),
            Targets=targets
        )
        template.add_resource(rule)

        for lambda_ in target_lambdas:
            template.add_resource(
                troposphere.awslambda.Permission(
                    utils.valid_cloudformation_name(
                        self.name,
                        'rule',
                        'permission'
                    ),
                    Action="lambda:InvokeFunction",
                    FunctionName=self.get_destination_arn(lambda_),
                    Principal="events.amazonaws.com",
                    SourceArn=troposphere.GetAtt(
                        rule, 'Arn'
                    ),
                )
            )
