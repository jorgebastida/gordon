import re
from collections import defaultdict

import troposphere

from . import base
from gordon import exceptions
from gordon import utils
from gordon.contrib.s3.resources import (S3BucketNotificationConfiguration,
    NotificationConfiguration, KeyFilter)


class BucketNotificationConfiguration(base.BaseResource):

    required_settings = (
        'bucket',
        'notifications',
    )

    def get_function_name(self):
        """Returns a reference to the lambda which will process this stream."""
        return self.project.reference(
            self.settings.get('lambda')
        )

    def register_resources_template(self, template):
        extra = defaultdict(list)

        notifications_map = {
            'lambda': 'LambdaFunctionConfigurations',
            'queue': 'QueueConfigurations',
            'topic': 'TopicConfigurations',

        }

        top_events_for_bucket = set()
        sub_events_for_top = defaultdict(list)

        for notification in self.settings.get('notifications', []):

            notification_type = set(('lambda', 'topic', 'queue')) & set(notification.keys())

            if len(notification_type) != 1:
                raise exceptions.ResourceValidationError("""You need to define
                either a lamda, a queue or a topic as destination of your
                notification {}""".format(notification))

            if 'id' not in notification:
                raise exceptions.ResourceValidationError("""You need to define
                an id which identifies the notification {}""".format(notification))

            if 'events' in notification and notification['events']:
                for event in notification['events']:
                    event_match = re.match(r's3\:(\w+|\*)(?:\:(\w+|\*))?', event)
                    if event_match:
                        top, sub = event_match.groups()
                        if top in top_events_for_bucket or \
                           top in sub_events_for_top or\
                           sub in sub_events_for_top.get(top, []):
                           raise exceptions.ResourceValidationError("""Event
                           {} overlaps with some other event registered for the
                           same bucket.""".format(event))
                        else:
                            top_events_for_bucket.add(top)
                            sub_events_for_top[top].append(sub)
                    else:
                        raise exceptions.ResourceValidationError("""Invalid
                        event {}""".format(event))
            else:
                raise exceptions.ResourceValidationError("""You need to define
                a list of events for notification {}""".format(notification))

            filters = []
            for f in notification.get('filters', []):
                filters.append(
                    KeyFilter(
                        Name=f.keys()[0],
                        Value=f.values()[0]
                    )
                )

            extra[notifications_map[list(notification_type)[0]]].append(
                NotificationConfiguration(
                    Id=troposphere.Join('-', ['gordon', self.settings.get('id')]),
                    DestinationArn=notification.get(list(notification_type)[0]),
                    Events=notification['events'],
                    KeyFilters=filters
                )
            )

        extra = dict([[k, v] for k, v in extra.iteritems() if v])

        template.add_resource(
            S3BucketNotificationConfiguration.create_with(
                utils.valid_cloudformation_name(self.name),
                lambda_arn=troposphere.GetAtt(
                    self.project.reference('s3.bucket_notification_configuration'), 'Arn'
                ),
                Bucket=self.settings.get('bucket'),
                **extra
            )
        )

    def validate(self):
        for resource in self.project.get_resources():

            if not isinstance(resource, self.__class__):
                pass

            if resource.bucket == self.bucket:
                raise exceptions.ResourceValidationError("""Both resources
                '{}' and '{}', registers notifications for the bucket '{}'.
                Because AWS API limitations we need you to register all
                notifications of one bucket in the same resource.
                """.format(self, resource, self.bucket))
