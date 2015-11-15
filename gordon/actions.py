import os
import json
import hashlib

import boto3

from gordon import utils


class Serializable(object):
    """Base Serializable abstractions we'll use to serialize actions and
    properties included in gordon's custom templates.

    Serializable objects must define a list of properties they care about
    using the following format:

    properties = (
        (NAME, DEFAULT_VALUE, REQUIRED),
        ...
    )
    """

    properties = ()

    def __init__(self, **kwargs):
        for key, default, required in self.properties:
            if key in kwargs:
                value = kwargs[key]
            elif required:
                raise exceptions.ActionRequiredPropertyError(self.__class__.__name__, key)
            else:
                value = default
                if type(value) is type:
                    value = value()
            setattr(self, key, value)

    def serialize(self):
        data = dict([[k, getattr(self, k, None)] for k, _, _ in self.properties])
        data['_type'] = self.__class__.__name__
        return self._serialize(data)

    def _serialize(self, obj):
        if hasattr(obj, 'serialize'):
            return obj.serialize()
        elif isinstance(obj, dict):
            return dict((k, self._serialize(v)) for k, v in obj.iteritems())
        elif hasattr(obj, '__iter__'):
            return [self._serialize(v) for v in obj]
        return obj

    def to_json(self, *args, **kwargs):
        return json.dumps(self.serialize(), *args, **kwargs)

    @classmethod
    def from_dict(cls, data):
        def _unserialize(data):
            if isinstance(data, dict) and '_type' in data:
                params = dict([[k, _unserialize(v)] for k, v in data.iteritems()])
                return globals()[data['_type']](**params)
            elif isinstance(data, dict):
                return dict([[k, _unserialize(v)] for k, v in data.iteritems()])
            elif hasattr(data, '__iter__'):
                return [_unserialize(e) for e in data]
            else:
                return data
        return _unserialize(data)


class Ref(Serializable):
    properties = (
        ('name', '', True),
    )


class GetAttr(Serializable):

    properties = (
        ('action', '', True),
        ('attr', '', True),
    )


class Parameter(Serializable):
    properties = (
        ('name', '', True),
        ('default', '', False),
    )


class Output(Serializable):
    properties = (
        ('name', '', True),
        ('default', '', False),
        ('value', '', True),
    )


class ActionsTemplate(Serializable):
    properties = (
        ('actions', list, False),
        ('parameters', dict, False),
        ('outputs', dict, False),
        ('parallelizable', True, False),
    )

    def add(self, action):
        self.actions.append(action)

    def add_parameter(self, parameter):
        self.parameters[parameter.name] = parameter

    def add_output(self, output):
        self.outputs[output.name] = output

    def apply(self, context, project):
        action_outputs = {}
        for action in self.actions:
            action_outputs[action.name] = action.apply(context, project)

        outputs = {}
        for name, output in self.outputs.iteritems():
            if isinstance(output.value, GetAttr):
                value = action_outputs[output.value.action].get(output.value.attr, output.default)
            outputs[name] = value
        return outputs

    def __nonzero__(self):
        return bool(self.actions)


class BaseAction(Serializable):

    def apply(self):
        return {}

    def _get(self, name, context):
        value = getattr(self, name, None)
        if isinstance(value, Ref):
            value = context[value.name]
        return value


class UploadToS3(BaseAction):
    """Uploads ``filename`` to ``bucket/key``."""

    properties = (
        ('name', '', True),
        ('bucket', '', True),
        ('key', '', True),
        ('filename', '', True),
    )

    def apply(self, context, project):
        # Check if this file needs to get uploaded or not. In order to do so,
        # we could rely on ETAG for normal files, but one of the mainline
        # cases of gordon is to upload .zip files, and identical source folders
        # don't have consistent checksums when you zip them, so we need to
        # workaround this by generating our own checksum uppon creation and
        # leave a .metadata file inside the zip file.
        # If the file is not .zip file, we always upload the file.
        self.project = project
        self.context = context
        self.bucket = self._get('bucket', self.context)
        self.key = self._get('key', self.context)

        self.filename = os.path.join(
            project.build_path,
            self._get('filename', context)
        )

        if self.filename.endswith('.zip'):
            return self.apply_zip()
        return self.apply_general()

    def apply_general(self, metadata=None):
        print "Uploading", self.name, self.bucket, self.key
        s3 = boto3.resource('s3')
        obj = s3.Object(self.bucket, self.key)

        extraargs = None
        if metadata:
            extraargs = {'Metadata': metadata}

        obj.upload_file(self.filename, ExtraArgs=extraargs)
        return self.output(obj.version_id)

    def output(self, version):
        return {
            's3url': 'https://s3-{}.amazonaws.com/{}/{}'.format(
                self.project.region,
                self.bucket,
                self.key
            ),
            's3version': version
        }

    def apply_zip(self):
        s3client = boto3.client('s3')
        try:
            obj = s3client.get_object(Bucket=self.bucket, Key=self.key)
        except Exception, exc:
            obj = None

        # If there is a file in this key, check if the attached metadata sha1
        # matches with the sha1 inside the file zip
        zipmetadata = utils.get_zip_metadata(self.filename)
        if obj:
            if zipmetadata.get('sha1') and zipmetadata.get('sha1') == obj['Metadata'].get('sha1'):
                print "Local .zip metadata and current S3 file metadata are equal!"
                return self.output(obj['VersionId'])
            else:
                print "Local .zip metadata and current S3 file metadata are NOT equal!"
        return self.apply_general(metadata=zipmetadata)
