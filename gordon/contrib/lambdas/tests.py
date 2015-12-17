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
from . import alias
from . import version


class TestContribLambdas(unittest.TestCase):

    @patch('gordon.contrib.lambdas.alias.send')
    @patch('gordon.contrib.lambdas.alias.boto3.client')
    def test_alias_create(self, boto3_client, send_mock):
        client = Mock()
        boto3_client.return_value = client
        context = MockContext()
        event = {
            'RequestType': 'Create',
            'ResourceProperties': {
                'Name': 'alias_name',
                'FunctionName': 'function_name',
                'FunctionVersion': 'function_version',
                'Description': "description"
            }
        }
        client.get_alias.side_effect = ClientError(
            error_response={'Error': {'Code': 'ResourceNotFoundException'}},
            operation_name='get_alias'
        )
        client.create_alias.return_value = {'AliasArn': 'alias_arn'}

        alias.handler(event, context)

        client.create_alias.assert_called_once_with(
            FunctionName='function_name',
            Name='alias_name',
            FunctionVersion='function_version',
            Description='description'
        )

        send_mock.assert_called_once_with(
            event, context, SUCCESS, response_data={'Arn': 'alias_arn'}
        )

    @patch('gordon.contrib.lambdas.alias.send')
    @patch('gordon.contrib.lambdas.alias.boto3.client')
    def test_alias_update(self, boto3_client, send_mock):
        client = Mock()
        boto3_client.return_value = client
        context = MockContext()
        event = {
            'RequestType': 'Update',
            'ResourceProperties': {
                'Name': 'alias_name',
                'FunctionName': 'function_name',
                'FunctionVersion': 'function_version',
                'Description': "description"
            }
        }
        client.get_alias.return_value = True
        client.update_alias.return_value = {'AliasArn': 'alias_arn'}

        alias.handler(event, context)

        client.update_alias.assert_called_once_with(
            FunctionName='function_name',
            Name='alias_name',
            FunctionVersion='function_version',
            Description='description'
        )

        send_mock.assert_called_once_with(
            event, context, SUCCESS, response_data={'Arn': 'alias_arn'}
        )

    @patch('gordon.contrib.lambdas.alias.send')
    @patch('gordon.contrib.lambdas.alias.boto3.client')
    def test_alias_delete(self, boto3_client, send_mock):
        client = Mock()
        boto3_client.return_value = client
        context = MockContext()
        event = {
            'RequestType': 'Delete',
            'ResourceProperties': {
                'Name': 'alias_name',
                'FunctionName': 'function_name',
                'FunctionVersion': 'function_version',
                'Description': "description"
            }
        }
        client.get_alias.return_value = True
        client.update_alias.return_value = {'AliasArn': 'alias_arn'}

        alias.handler(event, context)

        client.update_alias.assert_not_called()
        client.create_alias.assert_not_called()
        send_mock.assert_called_once_with(
            event, context, SUCCESS
        )


class TestContribVersion(unittest.TestCase):

    @patch('gordon.contrib.lambdas.version.send')
    @patch('gordon.contrib.lambdas.version.boto3.client')
    def test_version_create(self, boto3_client, send_mock):
        client = Mock()
        boto3_client.return_value = client
        context = MockContext()
        event = {
            'RequestType': 'Create',
            'ResourceProperties': {
                'FunctionName': 'function_name',
            }
        }

        client.get_function.return_value = {
            'Configuration': {
                'CodeSha256': '123'
            }
        }

        client.publish_version.return_value = {'Version': 'version123'}

        version.handler(event, context)

        client.publish_version.assert_called_once_with(
            FunctionName='function_name',
            CodeSha256='123'
        )

        send_mock.assert_called_once_with(
            event, context, SUCCESS, response_data={'Version': 'version123'}
        )

    @patch('gordon.contrib.lambdas.version.send')
    @patch('gordon.contrib.lambdas.version.boto3.client')
    def test_version_update(self, boto3_client, send_mock):
        client = Mock()
        boto3_client.return_value = client
        context = MockContext()
        event = {
            'RequestType': 'Update',
            'ResourceProperties': {
                'FunctionName': 'function_name',
            }
        }

        client.get_function.return_value = {
            'Configuration': {
                'CodeSha256': '123'
            }
        }

        client.publish_version.return_value = {'Version': 'version123'}

        version.handler(event, context)

        client.publish_version.assert_called_once_with(
            FunctionName='function_name',
            CodeSha256='123'
        )

        send_mock.assert_called_once_with(
            event, context, SUCCESS, response_data={'Version': 'version123'}
        )

    @patch('gordon.contrib.lambdas.version.send')
    @patch('gordon.contrib.lambdas.version.boto3.client')
    def test_version_delete(self, boto3_client, send_mock):
        client = Mock()
        boto3_client.return_value = client
        context = MockContext()
        event = {
            'RequestType': 'Delete',
            'ResourceProperties': {
                'FunctionName': 'function_name',
            }
        }

        version.handler(event, context)

        client.get_function.assert_not_called()
        client.publish_version.assert_not_called()
        send_mock.assert_called_once_with(event, context, SUCCESS)
