import sys
import unittest
import urllib2

try:
    from mock import patch, Mock, call
except ImportError:
    from unittest.mock import patch, Mock, call

from cfnresponse import SUCCESS, FAILED
from gordon.utils_tests import MockContext
from . import rest_api


class TestRestApi(unittest.TestCase):

    @patch('gordon.contrib.apigateway.rest_api.boto3.client')
    @patch('gordon.contrib.apigateway.rest_api.send')
    def test_create(self, send_mock, client_mock):
        client = Mock()
        client_mock.return_value = client
        client.create_rest_api.return_value = {
            'id': '12345'
        }

        event = {
            'RequestType': 'Create',
            'ResourceProperties': {
                'Name': 'my-api',
                'Description': 'My Api description'
            }
        }
        context = MockContext()

        rest_api.handler(event=event, context=context)

        client.create_rest_api.assert_called_once_with(
            name='my-api',
            description='My Api description',
        )

        send_mock.assert_called_once_with(
            event,
            context,
            SUCCESS,
            physical_resource_id='12345',
            response_data={'Id': '12345'}
        )

    @patch('gordon.contrib.apigateway.rest_api.boto3.client')
    @patch('gordon.contrib.apigateway.rest_api.send')
    def test_delete(self, send_mock, client_mock):
        client = Mock()
        client_mock.return_value = client

        event = {
            'RequestType': 'Delete',
            'ResourceProperties': {
                'Name': 'my-api',
                'Description': 'My Api description',
                'PhysicalResourceId': '12345'
            }
        }
        context = MockContext()

        rest_api.handler(event=event, context=context)

        client.delete_rest_api.assert_called_once_with(
            restApiId='12345',
        )

        send_mock.assert_called_once_with(
            event,
            context,
            SUCCESS
        )
