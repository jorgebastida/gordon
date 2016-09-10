import re
from collections import defaultdict, Counter

import six
import troposphere
from troposphere import sqs, sns, awslambda

from . import base
from gordon import exceptions
from gordon import utils
from gordon.actions import Ref
from gordon.contrib.s3.resources import (
    S3BucketNotificationConfiguration,
    NotificationConfiguration, KeyFilter
)


class BaseNotification(object):

    def __init__(self, bucket_notification_configuration, **kwargs):
        self.settings = kwargs
        self.bucket_notification_configuration = bucket_notification_configuration
        self.events = []

        # Validate all notifications have an id. This important because
        # we'll rely on this id to create/modify/delete notifactions
        if 'id' in self.settings:
            self.id = self.settings['id']
        else:
            raise exceptions.ResourceValidationError(
                (
                    "You need to define an id which identifies the "
                    "notification {}").format(self.settings)
                )

        # Validate that events is present, and that it contains valid values
        if 'events' in self.settings and self.settings['events']:
            for event in self.settings['events']:
                event_match = re.match(r's3\:(\w+|\*)(?:\:(\w+|\*))?', event)
                if event_match:
                    self.events.append([event] + list(event_match.groups()))
                else:
                    raise exceptions.ResourceValidationError(
                        "Invalid event {}".format(event)
                    )
        else:
            raise exceptions.ResourceValidationError(
                ("You need to define a list of events for the "
                 "notification {}").format(self.name)
            )

        # Validate that filters are a subset of (prefix, suffix) and keys
        # are not duplicated.
        _filters = self.settings.get('key_filters', {})
        if set(_filters.values()) > set(('prefix', 'suffix')):
            raise exceptions.ResourceValidationError(
                """You can't create filters for '{}'.""".format(
                    ', '.join(_filters)
                )
            )
        else:
            self.filters = [(k, v) for k, v in six.iteritems(_filters)]

    @classmethod
    def from_dict(cls, data, id, bucket_notification_configuration):
        notification_type = set(('lambda', 'topic', 'queue')) & set(data.keys())

        if len(notification_type) != 1:
            raise exceptions.ResourceValidationError(
                (
                    "You need to define either a lamda, a queue or a topic "
                    "as destination of your notification {}"
                ).format(bucket_notification_configuration)
            )

        return {'lambda': LambdaFunctionNotification,
                'queue': QueueNotification,
                'topic': TopicNotification}.get(
                    list(notification_type)[0])(
                        id=id,
                        bucket_notification_configuration=bucket_notification_configuration,
                        **data
                )

    def get_destination_arn(self):
        pass

    def register_destination_publish_permission(self, template):
        pass


class LambdaFunctionNotification(BaseNotification):
    api_property = 'LambdaFunctionConfigurations'

    def register_destination_publish_permission(self, template):
        template.add_resource(
            awslambda.Permission(
                utils.valid_cloudformation_name(
                    self.bucket_notification_configuration.name,
                    self.id,
                    'permission'
                ),
                Action="lambda:InvokeFunction",
                FunctionName=self.get_destination_arn(),
                Principal="s3.amazonaws.com",
                SourceAccount=troposphere.Ref(troposphere.AWS_ACCOUNT_ID),
                SourceArn=self.bucket_notification_configuration.get_bucket_arn()
            )
        )

    def get_destination_arn(self):
        return troposphere.Ref(
            self.bucket_notification_configuration.project.reference(
                utils.lambda_friendly_name_to_grn(
                    self.settings['lambda']
                )
            )
        )


class QueueNotification(BaseNotification):

    api_property = 'QueueConfigurations'

    def get_destination_arn(self):
        destination = self.settings['queue']
        region = troposphere.Ref(troposphere.AWS_REGION)

        if isinstance(destination, six.string_types):
            if destination.startswith('arn:aws:'):
                return destination
            account = troposphere.Ref(troposphere.AWS_ACCOUNT_ID)
        elif isinstance(destination, dict):
            account = destination['account_id']
            destination = destination['name']
        else:
            return destination

        return troposphere.Join(":", [
            "arn:aws:sqs",
            region,
            account,
            destination
        ])

    def get_destination_url(self):
        destination = self.settings['queue']
        region = troposphere.Ref(troposphere.AWS_REGION)

        if isinstance(destination, six.string_types):
            account = troposphere.Ref(troposphere.AWS_ACCOUNT_ID)
        elif isinstance(destination, dict):
            account = destination['account_id']
            destination = destination['name']
        else:
            return destination

        return troposphere.Join("", [
            "https://sqs.",
            region,
            ".amazonaws.com/",
            account,
            "/",
            destination
        ])

    def register_destination_publish_permission(self, template):
        template.add_resource(
            sqs.QueuePolicy(
                utils.valid_cloudformation_name(
                    self.bucket_notification_configuration.name,
                    self.id,
                    'permission'
                ),
                Queues=[self.get_destination_url()],
                PolicyDocument={
                    "Version": "2008-10-17",
                    "Id": "PublicationPolicy",
                    "Statement": [{
                        "Effect": "Allow",
                        "Principal": {
                          "AWS": "*"
                        },
                        "Action": ["sqs:SendMessage"],
                        "Resource": self.get_destination_arn(),
                        "Condition": {
                            "ArnEquals": {"aws:SourceArn": self.bucket_notification_configuration.get_bucket_arn()}
                        }
                    }]
                }
            )
        )


class TopicNotification(BaseNotification):
    api_property = 'TopicConfigurations'

    def get_destination_arn(self):
        destination = self.settings['topic']
        region = troposphere.Ref(troposphere.AWS_REGION)

        if isinstance(destination, six.string_types):
            if destination.startswith('arn:aws:'):
                return destination
            account = troposphere.Ref(troposphere.AWS_ACCOUNT_ID)
        elif isinstance(destination, dict):
            account = destination['account_id']
            destination = destination['name']
        else:
            return destination

        return troposphere.Join(":", [
            "arn:aws:sns",
            region,
            account,
            destination
        ])

    def register_destination_publish_permission(self, template):
        template.add_resource(
            sns.TopicPolicy(
                utils.valid_cloudformation_name(
                    self.bucket_notification_configuration.name,
                    self.id,
                    'permission'
                ),
                Topics=[self.get_destination_arn()],
                PolicyDocument={
                    "Version": "2008-10-17",
                    "Id": "PublicationPolicy",
                    "Statement": [{
                        "Effect": "Allow",
                        "Principal": {
                          "AWS": "*"
                        },
                        "Action": ["sns:Publish"],
                        "Resource": self.get_destination_arn(),
                        "Condition": {
                            "ArnEquals": {"aws:SourceArn": self.bucket_notification_configuration.get_bucket_arn()}
                        }
                    }]
                }
            )
        )


class BucketNotificationConfiguration(base.BaseResource):

    grn_type = 's3-bucket-notification'
    required_settings = (
        'bucket',
        'notifications',
    )

    def __init__(self, *args, **kwargs):
        super(BucketNotificationConfiguration, self).__init__(*args, **kwargs)
        self._notifications = {}

        for notification_id, notification_data in six.iteritems(self.settings.get('notifications', {})):
            self._notifications[notification_id] = BaseNotification.from_dict(
                    id=notification_id,
                    data=notification_data,
                    bucket_notification_configuration=self
            )

        self._validate_notifications()

    def get_bucket_arn(self):
        bucket_name = self.get_bucket_name()
        return troposphere.Join("", ["arn:aws:s3:::", bucket_name])

    def get_bucket_name(self):
        bucket = self.settings.get('bucket')
        if isinstance(bucket, troposphere.Ref):
            return bucket
        return bucket

    def _validate_notifications(self):
        # Validate that all key prefix/suffix filters for a bucket
        # don't overlap one to each other.
        all_filters = defaultdict(list)
        for notification_id, notification in six.iteritems(self._notifications):
            for name, value in notification.filters:
                all_filters[name].append(value)

        overlap_checks = {'prefix': 'startswith', 'suffix': 'endswith'}
        for filter_type, values in six.iteritems(all_filters):
            check = overlap_checks.get(filter_type)
            # Don't check fields that are Ref instances
            # since Refs aren't bound until apply
            if isinstance(check, Ref):
                continue
            overlaps = [sum([int(getattr(v, check)(z)) for z in values]) for v in values]
            if sum(overlaps) > len(values):
                raise exceptions.ResourceValidationError(
                    "One or more {} filters overlap one to each other {}.".format(
                        filter_type,
                        ', '.join(values)
                    )
                )

    def register_resources_template(self, template):

        extra = defaultdict(list)
        for notification_id, notification in six.iteritems(self._notifications):
            notification.register_destination_publish_permission(template)

            extra[notification.api_property].append(
                NotificationConfiguration(
                    Id=troposphere.Join('-', ['gordon', notification.id]),
                    DestinationArn=notification.get_destination_arn(),
                    Events=[e for e, _, _ in notification.events],
                    KeyFilters=[KeyFilter(Name=name, Value=value) for name, value in notification.filters]
                )
            )

        bucket_notification_configuration_lambda = 'lambda:contrib_s3:bucket_notification_configuration:current'
        template.add_resource(
            S3BucketNotificationConfiguration.create_with(
                utils.valid_cloudformation_name(self.name),
                DependsOn=[self.project.reference(bucket_notification_configuration_lambda)],
                lambda_arn=troposphere.Ref(self.project.reference(bucket_notification_configuration_lambda)),
                Bucket=self.get_bucket_name(),
                **dict([[k, v] for k, v in six.iteritems(extra) if v])
            )
        )

    def validate(self):
        """Validate that there are no any other resources in the project which
        try to register notifications for the same bucket than this resource"""
        for resource in \
                (r for r in self.project.get_resources() if isinstance(r, self.__class__) and r.bucket == self.bucket):
            raise exceptions.ResourceValidationError(
                ("Both resources '{}' and '{}', registers notifications for "
                 "the bucket '{}'. Because AWS API limitations we need you to "
                 "register all notifications of one bucket in the same "
                 "resource.").format(self, resource, self.bucket)
            )
