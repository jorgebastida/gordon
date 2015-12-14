import sys
import unittest
import urllib2

try:
    from mock import patch, Mock, call
except ImportError:
    from unittest.mock import patch, Mock, call

from gordon.actions import Parameter, ActionsTemplate, GetAttr, UploadToS3
from gordon import exceptions


class TestActions(unittest.TestCase):

    def test_basic_serializable(self):

        t = Parameter(name="Name", default="Default")
        s = t.serialize()
        self.assertEqual(s, {'_type': 'Parameter', 'name': 'Name', 'default': 'Default'})
        self.assertEqual(t, Parameter.from_dict(s))

        t = Parameter(name="Name")
        s = t.serialize()
        self.assertEqual(s, {'_type': 'Parameter', 'name': 'Name', 'default': ''})
        self.assertEqual(t, Parameter.from_dict(s))

        self.assertRaises(exceptions.PropertyRequiredError, Parameter)

    def test_complex_serializable(self):

        t = ActionsTemplate()
        s = t.serialize()
        self.assertEqual(s, {'_type': 'ActionsTemplate', 'actions': [], 'parameters': {}, 'outputs': {}, 'parallelizable': False})
        self.assertEqual(t, ActionsTemplate.from_dict(s))

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
    @patch('gordon.actions.utils.get_zip_metadata')
    def test_upload_to_s3(self, get_zip_metadata_mock, client_mock, resource_mock):
        client = Mock()
        resource = Mock()
        client_mock.return_value = client
        resource_mock.return_value = resource

        #
        # New file
        #
        client.get_object.side_effect = Exception()
        get_zip_metadata_mock.return_value = {'sha1': '123'}
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
        client.get_object.side_effect = None
        client.get_object.return_value = {'Metadata': {'sha1': '122'}}

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

        client.get_object.return_value = {'Metadata': {'sha1': '123'}, 'VersionId': 'version123'}

        u = UploadToS3(name='name', bucket='bucket', key='key', filename='filename.zip')
        output = u.apply(context, project)

        self.assertEqual(
            output,
            {'s3url': 'https://s3-eu-west-1.amazonaws.com/bucket/key', 's3version': 'version123'}
        )
        resource.Object.assert_not_called()
        resource.Object.return_value.upload_file.assert_not_called()
