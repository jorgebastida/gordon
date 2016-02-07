import unittest

try:
    from mock import patch, Mock
except ImportError:
    from unittest.mock import patch, Mock

from cfnresponse import SUCCESS, FAILED
from gordon.utils_tests import MockContext
from .bucket_notification_configuration import bucket_notification_configuration
from . import resources


class TestContribS3(unittest.TestCase):

    def test_validate_key_filter_name(self):
        self.assertEqual(resources.validate_key_filter_name('prefix'), 'prefix')
        self.assertEqual(resources.validate_key_filter_name('prefix'), 'prefix')
        self.assertRaises(ValueError, resources.validate_key_filter_name, 'aaa')

    def test_S3BucketNotificationConfiguration(self):
        conf = resources.S3BucketNotificationConfiguration(
            "Name",
            ServiceToken='service_token',
            Bucket='bucket',
        )
        self.assertRaises(ValueError, conf.validate)

        conf = resources.S3BucketNotificationConfiguration(
            "Name",
            ServiceToken='service_token',
            Bucket='bucket',
            TopicConfigurations=[
                resources.NotificationConfiguration(
                    Id='id',
                    DestinationArn='arn',
                    Events=['a']
                )
            ]
        )
        self.assertEqual(conf.validate(), None)

    def _test_bucket_notification_configuration(self, boto3_client, send_mock, request_type):
        client = Mock()
        boto3_client.return_value = client
        context = MockContext()
        event = {
            'RequestType': request_type,
            'ResourceProperties': {
                'Bucket': 'bucket',
                'LambdaFunctionConfigurations': [
                    {
                        'Id': 'lambda-id',
                        'DestinationArn': 'lambda-arn',
                        'Events': [
                            'event1',
                            'event2'
                        ],
                        'KeyFilters': [
                            'filters1'
                        ]
                    }
                ],
                'TopicConfigurations': [
                    {
                        'Id': 'topic-id',
                        'DestinationArn': 'topic-arn',
                        'Events': [
                            'event1',
                            'event2'
                        ],
                        'KeyFilters': [
                            'filters2'
                        ]
                    }
                ],
                'QueueConfigurations': [
                    {
                        'Id': 'topic-id',
                        'DestinationArn': 'topic-arn',
                        'Events': [
                            'event1',
                            'event2'
                        ],
                        'KeyFilters': []
                    }
                ]
            }
        }
        client.get_bucket_notification_configuration.return_value = {
            'LambdaFunctionConfigurations': [
                {
                    'Id': 'gordon-configuration'
                }
            ],
            'TopicConfigurations': [
                {
                    'Id': 'gordon-configuration'
                }
            ],
            'QueueConfigurations': [
            ],
        }

        bucket_notification_configuration.handler(event, context)

        client.put_bucket_notification_configuration.assert_called_once_with(
            Bucket='bucket',
            NotificationConfiguration={
                'LambdaFunctionConfigurations': [
                    {
                        'Id': 'lambda-id',
                        'LambdaFunctionArn': 'lambda-arn',
                        'Events': [
                            'event1',
                            'event2'
                        ],
                        'Filter': {
                            'Key': {
                                'FilterRules': [
                                    'filters1'
                                ]
                            }
                        }
                    }
                ],
                'TopicConfigurations': [
                    {
                        'Id': 'topic-id',
                        'TopicArn': 'topic-arn',
                        'Events': [
                            'event1',
                            'event2'
                        ],
                        'Filter': {
                            'Key': {
                                'FilterRules': [
                                    'filters2'
                                ]
                            }
                        }
                    }
                ],
                'QueueConfigurations': [
                    {
                        'Id': 'topic-id',
                        'QueueArn': 'topic-arn',
                        'Events': [
                            'event1',
                            'event2'
                        ],
                    }
                ]
            }
        )

        send_mock.assert_called_once_with(
            event, context, SUCCESS,
            physical_resource_id='bucket-bucket-notification-configuration'
        )

    @patch('gordon.contrib.s3.bucket_notification_configuration.bucket_notification_configuration.send')
    @patch('gordon.contrib.s3.bucket_notification_configuration.bucket_notification_configuration.boto3.client')
    def test_bucket_notification_configuration_create(self, boto3_client, send_mock):
        self._test_bucket_notification_configuration(boto3_client, send_mock, 'Create')

    @patch('gordon.contrib.s3.bucket_notification_configuration.bucket_notification_configuration.send')
    @patch('gordon.contrib.s3.bucket_notification_configuration.bucket_notification_configuration.boto3.client')
    def test_bucket_notification_configuration_update(self, boto3_client, send_mock):
        self._test_bucket_notification_configuration(boto3_client, send_mock, 'Update')

    @patch('gordon.contrib.s3.bucket_notification_configuration.bucket_notification_configuration.send')
    @patch('gordon.contrib.s3.bucket_notification_configuration.bucket_notification_configuration.boto3.client')
    def test_bucket_notification_configuration_delete(self, boto3_client, send_mock):
        client = Mock()
        boto3_client.return_value = client
        context = MockContext()
        event = {
            'RequestType': 'Delete',
            'ResourceProperties': {
                'Bucket': 'bucket',
            }
        }
        client.get_bucket_notification_configuration.return_value = {}

        bucket_notification_configuration.handler(event, context)

        client.put_bucket_notification_configuration.assert_called_once_with(
            Bucket='bucket',
            NotificationConfiguration={}
        )

        send_mock.assert_called_once_with(
            event, context, SUCCESS,
            physical_resource_id='bucket-bucket-notification-configuration'
        )

    @patch('gordon.contrib.s3.bucket_notification_configuration.bucket_notification_configuration.send')
    @patch('gordon.contrib.s3.bucket_notification_configuration.bucket_notification_configuration.boto3.client')
    def test_bucket_notification_configuration_existing_non_gordon_configuration(self, boto3_client, send_mock):
        client = Mock()
        boto3_client.return_value = client
        context = MockContext()
        event = {
            'RequestType': 'Create',
            'ResourceProperties': {
                'Bucket': 'bucket'
            }
        }

        client.get_bucket_notification_configuration.return_value = {
            'LambdaFunctionConfigurations': [
                {
                    'Id': 'custom-id'
                }
            ],
            'TopicConfigurations': [
                {
                    'Id': 'custom-id'
                }
            ],
            'QueueConfigurations': [
                {
                    'Id': 'custom-id'
                }
            ],
        }

        bucket_notification_configuration.handler(event, context)

        send_mock.assert_called_once_with(
            event, context, FAILED,
            physical_resource_id='bucket-bucket-notification-configuration',
            reason=("Bucket bucket contains a notification called custom-id "
                    "which was not created by gordon, hence the risk "
                    "of trying it to add/modify/delete new notifications. "
                    "Please check the documentation in order to understand "
                    "why gordon refuses to proceed.")
        )
