import unittest
import json

try:
    from mock import patch, Mock
except ImportError:
    from unittest.mock import patch, Mock

from gordon.actions import Parameter, ActionsTemplate, GetAttr, UploadToS3
from gordon import exceptions, protocols


class TestProtocols(unittest.TestCase):

    @patch('gordon.protocols.boto3.client')
    def test_kinesis_protocols(self, client_mock):
        paginate = client_mock.return_value.get_paginator.return_value.paginate
        paginate.return_value = [
            {'StreamNames': ['aaa', 'abb']},
            {'StreamNames': ['acc', 'abc']},
        ]

        # match
        self.assertRaises(exceptions.ProtocolNotFoundlError, protocols.kinesis_match, 'xxx')
        self.assertRaises(exceptions.ProtocolMultipleMatcheslError, protocols.kinesis_match, 'ab')
        self.assertEqual(protocols.kinesis_match('aa'), 'aaa')
        self.assertEqual(protocols.kinesis_match('bc$'), 'abc')

        # startswith
        self.assertRaises(exceptions.ProtocolNotFoundlError, protocols.kinesis_startswith, 'xxx')
        self.assertRaises(exceptions.ProtocolMultipleMatcheslError, protocols.kinesis_startswith, 'a')
        self.assertEqual(protocols.kinesis_startswith('aa'), 'aaa')

        # endswith
        self.assertRaises(exceptions.ProtocolNotFoundlError, protocols.kinesis_endswith, 'xxx')
        self.assertRaises(exceptions.ProtocolMultipleMatcheslError, protocols.kinesis_endswith, 'c')
        self.assertEqual(protocols.kinesis_endswith('b'), 'abb')

    @patch('gordon.protocols.boto3.client')
    def test_dynamodb_protocols(self, client_mock):
        paginate = client_mock.return_value.get_paginator.return_value.paginate
        paginate.return_value = [
            {'TableNames': ['aaa', 'abb']},
            {'TableNames': ['acc', 'abc']},
        ]

        # match
        self.assertRaises(exceptions.ProtocolNotFoundlError, protocols.dynamodb_match, 'xxx')
        self.assertRaises(exceptions.ProtocolMultipleMatcheslError, protocols.dynamodb_match, 'ab')
        self.assertEqual(protocols.dynamodb_match('aa'), 'aaa')
        self.assertEqual(protocols.dynamodb_match('bc$'), 'abc')

        # startswith
        self.assertRaises(exceptions.ProtocolNotFoundlError, protocols.dynamodb_startswith, 'xxx')
        self.assertRaises(exceptions.ProtocolMultipleMatcheslError, protocols.dynamodb_startswith, 'a')
        self.assertEqual(protocols.dynamodb_startswith('aa'), 'aaa')

        # endswith
        self.assertRaises(exceptions.ProtocolNotFoundlError, protocols.dynamodb_endswith, 'xxx')
        self.assertRaises(exceptions.ProtocolMultipleMatcheslError, protocols.dynamodb_endswith, 'c')
        self.assertEqual(protocols.dynamodb_endswith('b'), 'abb')

    @patch('gordon.protocols.boto3.client')
    def test_dynamodb_stream_protocols(self, client_mock):
        client_mock.return_value.list_streams.return_value = {
            'Streams': [
                {'TableName': 'aaa', 'StreamArn': 'aaa'},
                {'TableName': 'abb', 'StreamArn': 'abb'},
                {'TableName': 'acc', 'StreamArn': 'acc'},
                {'TableName': 'abc', 'StreamArn': 'abc'}
            ]
        }

        # match
        self.assertRaises(exceptions.ProtocolNotFoundlError, protocols.dynamodb_stream_match, 'xxx')
        self.assertRaises(exceptions.ProtocolMultipleMatcheslError, protocols.dynamodb_stream_match, 'ab')
        self.assertEqual(protocols.dynamodb_stream_match('aa'), 'aaa')
        self.assertEqual(protocols.dynamodb_stream_match('bc$'), 'abc')

        # startswith
        self.assertRaises(exceptions.ProtocolNotFoundlError, protocols.dynamodb_stream_startswith, 'xxx')
        self.assertRaises(exceptions.ProtocolMultipleMatcheslError, protocols.dynamodb_stream_startswith, 'a')
        self.assertEqual(protocols.dynamodb_stream_startswith('aa'), 'aaa')

        # endswith
        self.assertRaises(exceptions.ProtocolNotFoundlError, protocols.dynamodb_stream_endswith, 'xxx')
        self.assertRaises(exceptions.ProtocolMultipleMatcheslError, protocols.dynamodb_stream_endswith, 'c')
        self.assertEqual(protocols.dynamodb_stream_endswith('b'), 'abb')


class TestActions(unittest.TestCase):

    def test_basic_serializable(self):

        t = Parameter(name="Name", default="Default")
        s = t.serialize()
        self.assertEqual(s, {'_type': 'Parameter', 'name': 'Name', 'default': 'Default'})
        self.assertEqual(t, Parameter.from_dict(s))
        self.assertEqual(json.loads(t.to_json()), json.loads('{"default": "Default", "_type": "Parameter", "name": "Name"}'))

        t = Parameter(name="Name")
        s = t.serialize()
        self.assertEqual(s, {'_type': 'Parameter', 'name': 'Name', 'default': ''})
        self.assertEqual(t, Parameter.from_dict(s))

        self.assertRaises(exceptions.PropertyRequiredError, Parameter)

    def test_complex_serializable(self):

        t = ActionsTemplate()
        s = t.serialize()
        self.assertEqual(
            s,
            {
                '_type': 'ActionsTemplate',
                'actions': [],
                'parameters': {},
                'outputs': {},
                'parallelizable': False
            }
        )
        self.assertEqual(t, ActionsTemplate.from_dict(s))
        self.assertFalse(t)

    def test_actions_template(self):
        context, project = Mock(), Mock()
        action = Mock()
        action.name = 'upload'
        action.apply.return_value = {'version': '1234'}

        parameter = Mock()
        parameter.name = "name"

        output = Mock()
        output.name = "version"
        output.value = GetAttr(action='upload', attr='version')
        output2 = Mock()
        output2.name = "pi"
        output2.value = "3.1416"

        at = ActionsTemplate()
        at.add(action)
        at.add_parameter(parameter)
        at.add_output(output)
        at.add_output(output2)

        self.assertEqual(at.apply(context, project), {'version': '1234', 'pi': '3.1416'})

    @patch('gordon.actions.boto3.resource')
    @patch('gordon.actions.boto3.client')
    @patch('gordon.actions.utils.get_file_hash')
    def test_upload_to_s3(self, get_file_hash_mock, client_mock, resource_mock):
        client = Mock()
        resource = Mock()
        client_mock.return_value = client
        resource_mock.return_value = resource

        #
        # New file
        #
        client.head_object.side_effect = Exception()
        get_file_hash_mock.return_value = '123'
        resource.Object.return_value.version_id = 'version123'
        context = Mock()
        project = Mock(region='eu-west-1', build_path='_build')

        u = UploadToS3(name='name', bucket='bucket', key='key', filename='filename.zip')
        output = u.apply(context, project)

        self.assertEqual(
            output,
            {'s3url': 'https://s3-eu-west-1.amazonaws.com/bucket/key', 's3version': 'version123'}
        )
        resource.Object.assert_called_once_with(
            'bucket', 'key'
        )
        resource.Object.return_value.upload_file.assert_called_once_with(
            '_build/filename.zip',
            ExtraArgs={'Metadata': {'sha1': '123'}}
        )

        #
        # Existing file, but different hash
        #
        resource.Object.reset_mock()
        resource.Object.return_value.upload_file.reset_mock()
        client.head_object.side_effect = None
        client.head_object.return_value = {'Metadata': {'sha1': '122'}}

        u = UploadToS3(name='name', bucket='bucket', key='key', filename='filename.zip')
        output = u.apply(context, project)

        self.assertEqual(
            output,
            {'s3url': 'https://s3-eu-west-1.amazonaws.com/bucket/key', 's3version': 'version123'}
        )
        resource.Object.assert_called_once_with(
            'bucket', 'key'
        )
        resource.Object.return_value.upload_file.assert_called_once_with(
            '_build/filename.zip',
            ExtraArgs={'Metadata': {'sha1': '123'}}
        )

        #
        # Existing file, same hash
        #
        resource.Object.reset_mock()
        resource.Object.return_value.upload_file.reset_mock()

        client.head_object.return_value = {'Metadata': {'sha1': '123'}, 'VersionId': 'version123'}

        u = UploadToS3(name='name', bucket='bucket', key='key', filename='filename.zip')
        output = u.apply(context, project)

        self.assertEqual(
            output,
            {'s3url': 'https://s3-eu-west-1.amazonaws.com/bucket/key', 's3version': 'version123'}
        )
        resource.Object.assert_not_called()
        resource.Object.return_value.upload_file.assert_not_called()
