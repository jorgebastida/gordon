import sys
import unittest
import urllib2

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

try:
    from mock import patch, Mock, call
except ImportError:
    from unittest.mock import patch, Mock, call

from gordon.contrib.utils import gordon_sleep


class TestGordonContribUtils(unittest.TestCase):

    def _event(self):
        return {
            'StackId': 'stack_id',
            'RequestId': 'request_id',
            'LogicalResourceId': 'logical_resource_id',
            'ResponseURL': 'http://localhost/response'
        }

    def _context(self):
        return {
            'logStreamName': 'log_stream_name'
        }

    @patch('urllib2.OpenerDirector.open')
    def test_cfn_send_success(self, open_mock):
        open_mock.return_value = Mock()
        open_mock.return_value.msg = 'OK'
        open_mock.return_value.getcode.return_value = 200
        response = gordon_sleep.send(
            event=self._event(),
            context=self._context(),
            responseStatus='response_status',
            responseData='response_data',
        )
        self.assertTrue(response)

    @patch('urllib2.OpenerDirector.open')
    def test_cfn_send_error(self, open_mock):

        class MockHTTPError(urllib2.HTTPError):
            def __init__(self, code=503):
                self.code = code

        open_mock.side_effect = MockHTTPError
        response = gordon_sleep.send(
            event=self._event(),
            context=self._context(),
            responseStatus='response_status',
            responseData='response_data',
        )
        self.assertFalse(response)
