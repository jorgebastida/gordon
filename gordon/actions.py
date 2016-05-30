# -*- coding: utf-8 -*-
import os
import json
import tempfile
import zipfile
import shutil
from collections import Iterable

import six
import boto3
import troposphere
from clint.textui import colored, puts

from gordon import utils, exceptions


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
                raise exceptions.PropertyRequiredError(self.__class__.__name__, key)
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
            return dict((k, self._serialize(v)) for k, v in six.iteritems(obj))
        elif isinstance(obj, troposphere.Ref):
            return {'_type': 'Ref', 'name': obj.data['Ref']}
        elif isinstance(obj, Iterable) and not isinstance(obj, six.string_types):
            return [self._serialize(v) for v in obj]
        return obj

    def to_json(self, *args, **kwargs):
        kwargs['sort_keys'] = True
        return json.dumps(self.serialize(), *args, **kwargs)

    def __eq__(self, obj):
        return all([getattr(self, p) == getattr(obj, p) for p, _, _ in self.properties])

    @classmethod
    def from_dict(cls, data):
        def _unserialize(data):
            if isinstance(data, dict) and '_type' in data:
                params = dict([[k, _unserialize(v)] for k, v in six.iteritems(data)])
                return globals()[data['_type']](**params)
            elif isinstance(data, dict):
                return dict([[k, _unserialize(v)] for k, v in six.iteritems(data)])
            elif isinstance(data, Iterable) and not isinstance(data, six.string_types):
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
        ('parallelizable', False, False),
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
        for name, output in six.iteritems(self.outputs):
            if isinstance(output.value, GetAttr):
                value = action_outputs[output.value.action].get(output.value.attr, output.default)
            else:
                value = output.value
            outputs[name] = value
        return outputs

    def __bool__(self):
        return bool(self.actions)

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
        """
        Check if this file needs to get uploaded or not. In order to do so,
        we could rely on ETAG for normal files, but one of the mainline
        cases of gordon is to upload .zip files, and identical source folders
        don't have consistent hashes when you zip them, so we need to
        workaround this by generating our own hash by reading the zip content
        in a particular order."""

        self.project = project
        self.context = context
        self.bucket = self._get('bucket', self.context)
        self.key = self._get('key', self.context)

        self.filename = self._friendly_name = os.path.join(
            project.build_path,
            self._get('filename', context)
        )

        self.filename = self.prepare_file(self.filename)

        s3client = boto3.client('s3')
        try:
            obj = s3client.head_object(Bucket=self.bucket, Key=self.key)
        except Exception:
            obj = None

        # Calculate the hash of this file
        file_hash = utils.get_file_hash(self.filename)

        # If the object is present, and the hash in the metadata is the same
        # we don't need to upload it.
        if obj and file_hash == obj['Metadata'].get('sha1'):
            self._success(file_hash, project.puts)
            if self.project.debug:
                project.puts(colored.white(u"✸ File with hash {} already present in {}/{}.".format(
                    file_hash[:8], self.bucket, self.key))
                )
            return self.output(obj['VersionId'])

        # If the key is not present or the hash doesn't match, we need to upload it.
        if self.project.debug:
            project.puts(colored.white(u"✸ Uploading file with hash {} to {}/{}.".format(
                file_hash[:8], self.bucket, self.key))
            )

        obj = boto3.resource('s3').Object(self.bucket, self.key)
        obj.upload_file(self.filename, ExtraArgs={'Metadata': {'sha1': file_hash}})
        self._success(file_hash, project.puts)
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

    def prepare_file(self, filename):
        return filename

    def _success(self, metadata, puts_function):
        puts_function(
            colored.green(
                u"✓ {} ({})".format(
                    os.path.relpath(self._friendly_name, self.project.build_path), metadata[:8]
                )
            )
        )


def enrich_references(obj, context):
    if isinstance(obj, dict):
        return dict((k, enrich_references(v, context)) for k, v in six.iteritems(obj))
    elif isinstance(obj, Ref):
        return context[obj.name]
    elif isinstance(obj, Iterable) and not isinstance(obj, six.string_types):
        return [enrich_references(v, context) for v in obj]
    return obj


class InjectContextAndUploadToS3(UploadToS3):

    properties = UploadToS3.properties + (
        ('context_to_inject', None, False),
        ('context_destinaton', None, False),
    )

    def prepare_file(self, filename):
        context_to_inject = enrich_references(self.context_to_inject or {}, self.context)
        context_destinaton = self.context_destinaton or '.context'
        _, tmpfile = tempfile.mkstemp(suffix='.{}'.format(self.filename.rsplit('.', 1)[1]))
        shutil.copyfile(self.filename, tmpfile)
        zfile = zipfile.ZipFile(tmpfile, 'a')

        context_info = zipfile.ZipInfo(context_destinaton)
        context_info.external_attr = 0o444 << 16
        zfile.writestr(context_info, json.dumps(context_to_inject))
        zfile.close()
        return tmpfile
