import sys
import unittest
import urllib2

try:
    from mock import patch, Mock, call
except ImportError:
    from unittest.mock import patch, Mock, call

from botocore.exceptions import ClientError
from cfnresponse import SUCCESS
from gordon.utils_tests import MockContext
from .rule import rule


class TestContribEvents(unittest.TestCase):

    @patch('gordon.contrib.events.rule.rule.send')
    @patch('gordon.contrib.events.rule.rule.boto3.client')
    def test_rule_create(self, boto3_client, send_mock):
        client = Mock()
        boto3_client.return_value = client
        context = MockContext()
        event = {
            'RequestType': 'Create',
            'ResourceProperties': {
                'RuleName': 'rule_name',
                'ScheduleExpression': 'cron(0 20 * * ? *)',
                'State': 'ENABLED',
                'Description': 'My description',
            }
        }
        client.get_rule.side_effect = ClientError(
            error_response={'Error': {'Code': 'ResourceNotFoundException'}},
            operation_name='get_rule'
        )
        client.put_rule.return_value = {'RuleArn': 'rule_arn'}

        rule.handler(event, context)

        client.put_rule.assert_called_once_with(
            Name='rule_name',
            State='ENABLED',
            ScheduleExpression='cron(0 20 * * ? *)',
            EventPattern='',
            Description='My description',
            RoleArn=''
        )

        send_mock.assert_called_once_with(
            event, context, SUCCESS, response_data={'Arn': 'rule_arn'}
        )

    @patch('gordon.contrib.events.rule.rule.send')
    @patch('gordon.contrib.events.rule.rule.boto3.client')
    def test_rule_update(self, boto3_client, send_mock):
        client = Mock()
        boto3_client.return_value = client
        context = MockContext()
        event = {
            'RequestType': 'Update',
            'ResourceProperties': {
                'RuleName': 'rule_name',
                'ScheduleExpression': 'cron(0 20 * * ? *)',
                'State': 'ENABLED',
                'Description': 'My description',
            }
        }
        client.get_rule.return_value = True
        client.put_rule.return_value = {'RuleArn': 'rule_arn'}

        rule.handler(event, context)

        client.put_rule.assert_called_once_with(
            Name='rule_name',
            State='ENABLED',
            ScheduleExpression='cron(0 20 * * ? *)',
            EventPattern='',
            Description='My description',
            RoleArn=''
        )

        send_mock.assert_called_once_with(
            event, context, SUCCESS, response_data={'Arn': 'rule_arn'}
        )

    @patch('gordon.contrib.events.rule.rule.send')
    @patch('gordon.contrib.events.rule.rule.boto3.client')
    def test_rule_delete(self, boto3_client, send_mock):
        client = Mock()
        boto3_client.return_value = client
        context = MockContext()
        event = {
            'RequestType': 'Delete',
            'ResourceProperties': {
                'RuleName': 'rule_name',
                'ScheduleExpression': 'cron(0 20 * * ? *)',
                'State': 'ENABLED',
                'Description': 'My description',
            }
        }
        client.get_rule.return_value = True
        client.put_rule.return_value = {'RuleArn': 'rule_arn'}

        rule.handler(event, context)

        client.put_rule.assert_not_called()
        send_mock.assert_called_once_with(
            event, context, SUCCESS
        )
