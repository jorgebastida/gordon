import os
import re
import uuid
import json
import base64
import hashlib
import shutil
import unittest
from nose.plugins.attrib import attr
from nose.tools import nottest

import boto3

from gordon.bin import main as gordon
from gordon.utils import cd, generate_stack_name



class MockContext(object):

    def __init__(self, **kwargs):
        self.function_name = kwargs.pop('function_name', 'function_name')
        self.remaining_time_in_millis = kwargs.pop('remaining_time_in_millis', 100)
        self.function_version = kwargs.pop('function_version', '1.0')
        self.invoked_function_arn = kwargs.pop('invoked_function_arn', 'arn:...')
        self.memory_limit_in_mb = kwargs.pop('memory_limit_in_mb', 128)
        self.aws_request_id = kwargs.pop('aws_request_id', '123456789')
        self.log_group_name = kwargs.pop('log_group_name', 'log_group_name')
        self.log_stream_name = kwargs.pop('log_stream_name', 'log_stream_name')
        self.identity = kwargs.pop('identity', None)
        self.client_context = kwargs.pop('identity', None)

    def get_remaining_time_in_millis(self):
        return self.remaining_time_in_millis


def delete_s3_bucket(bucket_name):
    s3client = boto3.client('s3')

    versions = s3client.list_object_versions(Bucket=bucket_name).get('Versions', [])
    objects = [{'Key': o['Key'], 'VersionId': o['VersionId']} for o in versions]
    if objects:

        for obj in objects:
            print "  ", obj['Key']

        s3client.delete_objects(
            Bucket=bucket_name,
            Delete={'Objects': objects, 'Quiet': False}

        )

    s3client.delete_bucket(Bucket=bucket_name)


@nottest
def delete_test_stacks(name):
    client = boto3.client('cloudformation')
    paginator = client.get_paginator('describe_stacks')
    for stacks in paginator.paginate():
        for stack in stacks['Stacks']:
            print stack['StackName']
            if stack['StackName'].startswith(name) and\
               [t for t in stack['Tags'] if t['Key'] == 'GordonVersion']:

                # Empty S3 buckets
                s3client = boto3.client('s3')
                for resource in client.describe_stack_resources(StackName=stack['StackName'])['StackResources']:
                    if resource['ResourceType'] == 'AWS::S3::Bucket':
                        delete_s3_bucket(resource['PhysicalResourceId'])

                client.delete_stack(
                    StackName=stack['StackName']
                )


@attr('integration')
class BaseIntegrationTest(object):

    def __init__(self, *args, **kwargs):
        super(BaseIntegrationTest, self).__init__(*args, **kwargs)
        self.uid = 'gt{}'.format(hashlib.sha1(str(uuid.uuid4())).hexdigest()[:5])
        self.test_path = os.path.join('integration', self.test)
        self.extra_env = {}

    @property
    def test(self):
        return self.__class__.__module__.split('.', 1)[0]

    def test_project(self):
        steps = []
        for filename in os.listdir(self.test_path):
            match = re.match(r'(\d+)_(\w+)', filename)
            if match and os.path.isdir(os.path.join(self.test_path, filename)):
                steps.append((int(match.groups()[0]), filename))

        steps = sorted(steps, key=lambda x:x[0])
        for _, filename in steps:
            with cd(os.path.join(self.test_path, filename)):
                gordon(['gordon', 'build'])
                self._test_build()
                gordon([
                    'gordon',
                    'apply',
                    '--stage={}'.format(self.uid),
                ])
                self._test_apply()

    def _restore_context(self):
        os.environ.clear()
        os.environ.update(self._environ)

    def _clean_extra_env(self):
        self.extra_env = {}

    def _clean_build_path(self):
        build_path = os.path.join(self.test_path, '_build')
        if os.path.exists(build_path):
            shutil.rmtree(build_path)

    def setUp(self):
        self._environ = dict(os.environ)
        os.environ.update(self.extra_env)
        self.addCleanup(self._restore_context)
        self.addCleanup(delete_test_stacks, self.uid)
        self.addCleanup(self._clean_build_path)
        self.addCleanup(self._clean_extra_env)

    def _test_build(self):
        pass

    def _test_apply(self):
        pass

    def assert_stack_succeed(self, stack_name):
        name = generate_stack_name(self.uid, self.test, stack_name)
        client = boto3.client('cloudformation')
        stacks = client.describe_stacks(StackName=name)
        self.assertEqual(len(stacks['Stacks']), 1)
        stack = stacks['Stacks'][0]
        self.assertIn(stack['StackStatus'], ('CREATE_COMPLETE',))

    def get_lambda(self, function_name):
        client = boto3.client('lambda')
        matches = []
        for f in client.list_functions().get('Functions', []):
            name = f['FunctionName'].split('-')
            if name[0] == self.uid and function_name.startswith(name[-2]):
                matches.append(f)
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            raise KeyError("Ambiguous lambda {}".format(function_name))
        raise KeyError(function_name)

    def invoke_lambda(self, function_name, payload=None):
        client = boto3.client('lambda')
        return client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            LogType='Tail',
            Payload=json.dumps(payload or {}),
        )

    def assert_lambda_response(self, response, value):
        self.assertEqual(json.loads(response['Payload'].read()), value)

    def get_lambda_versions(self, function_name):
        client = boto3.client('lambda')
        versions = client.list_versions_by_function(
            FunctionName=function_name
        )['Versions']
        return dict([[v['Version'], v] for v in versions])

    def get_lambda_aliases(self, function_name):
        client = boto3.client('lambda')
        aliases = client.list_aliases(
            FunctionName=function_name
        )['Aliases']
        return dict([[a['Name'], a] for a in aliases])

    def create_kinesis_stream(self, uid_prefix=''):
        stream_name = '{}{}'.format(uid_prefix, self.uid)
        client = boto3.client('kinesis')
        client.create_stream(StreamName=stream_name, ShardCount=1)
        client.get_waiter('stream_exists').wait(StreamName=stream_name)
        self.addCleanup(client.delete_stream, StreamName=stream_name)
        return client.describe_stream(StreamName=stream_name)
