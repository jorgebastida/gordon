import troposphere

from .base import BaseResource
from gordon.contrib.events.resources import EventsRule, EventsTargets, Target
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
        return troposphere.GetAtt(
            self.get_function_name(),
            'Arn'
        )

    def register_resources_template(self, template):
        rule_resource_name = utils.valid_cloudformation_name(self.name, "Rule")
        rule_name = troposphere.Join(
            "-",
            [rule_resource_name, troposphere.Ref(troposphere.AWS_STACK_NAME)]
        )

        events_rule_lambda = 'lambda:contrib_events:rule:current'
        rule = EventsRule.create_with(
            rule_resource_name,
            DependsOn=[self.project.reference(events_rule_lambda)],
            lambda_arn=troposphere.GetAtt(
                self.project.reference(events_rule_lambda), 'Arn'
            ),
            Name=rule_name,
            ScheduleExpression=self.get_expression(),
            State=self.get_enabled(),
            Description=self.settings.get('description', '')
        )
        template.add_resource(rule)

        template.add_resource(
            troposphere.awslambda.Permission(
                utils.valid_cloudformation_name(
                    self.name,
                    'permission'
                ),
                Action="lambda:InvokeFunction",
                FunctionName=self.get_destination_arn(),
                Principal="events.amazonaws.com",
                SourceArn=troposphere.GetAtt(
                    rule, 'Arn'
                ),
                SourceAccount=troposphere.Ref(troposphere.AWS_ACCOUNT_ID),
            )
        )

        events_targets_lambda = 'lambda:contrib_events:target:current'
        target = EventsTargets.create_with(
            utils.valid_cloudformation_name(self.name, "EventsTargets"),
            DependsOn=[
                self.project.reference(events_targets_lambda),
                rule_resource_name
            ],
            lambda_arn=troposphere.GetAtt(
                self.project.reference(events_targets_lambda), 'Arn'
            ),
            Rule=rule_name,
            Targets=[
                Target(
                    Id=self.get_function_name(),
                    Arn=self.get_destination_arn()
                )
            ]
        )
        template.add_resource(target)
