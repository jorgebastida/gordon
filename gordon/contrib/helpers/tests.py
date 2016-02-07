import unittest

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from cfnresponse import SUCCESS
from gordon.utils_tests import MockContext
from .sleep import sleep


class TestContribHelpers(unittest.TestCase):

    @patch('gordon.contrib.helpers.sleep.sleep.send')
    @patch('time.sleep')
    def test_sleep_create(self, sleep_mock, send_mock):
        context = MockContext()
        event = {
            'RequestType': 'Create',
            'ResourceProperties': {
                'Time': 1
            }
        }
        sleep.handler(event, context)
        send_mock.assert_called_once_with(event, context, SUCCESS)
        sleep_mock.assert_called_once_with(1)

    @patch('gordon.contrib.helpers.sleep.sleep.send')
    @patch('time.sleep')
    def test_sleep_update(self, sleep_mock, send_mock):
        context = MockContext()
        event = {
            'RequestType': 'Update',
            'ResourceProperties': {
                'Time': 1
            }
        }
        sleep.handler(event, context)
        send_mock.assert_called_once_with(event, context, SUCCESS)
        sleep_mock.assert_called_once_with(1)

    @patch('gordon.contrib.helpers.sleep.sleep.send')
    @patch('time.sleep')
    def test_sleep_delete(self, sleep_mock, send_mock):
        context = MockContext()
        event = {
            'RequestType': 'Delete',
            'ResourceProperties': {
                'Time': 1
            }
        }
        sleep.handler(event, context)
        send_mock.assert_called_once_with(event, context, SUCCESS)
        sleep_mock.assert_not_called()
