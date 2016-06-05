import os
import uuid
import json
import hashlib
import random
import shutil
import unittest
from nose.plugins.attrib import attr
from nose.tools import nottest
import tempfile

import six
import boto3

from gordon.bin import main as gordon
from gordon.utils import cd, generate_stack_name, delete_s3_bucket, Capturing


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


@nottest
def delete_test_stacks(name):
    client = boto3.client('cloudformation')
    paginator = client.get_paginator('describe_stacks')
    for stacks in paginator.paginate():
        for stack in stacks['Stacks']:
            print(stack['StackName'])
            if stack['StackName'].startswith(name) and\
               [t for t in stack['Tags'] if t['Key'] == 'GordonVersion']:
                for resource in client.describe_stack_resources(StackName=stack['StackName'])['StackResources']:
                    if resource['ResourceType'] == 'AWS::S3::Bucket':
                        delete_s3_bucket(resource['PhysicalResourceId'], dry_run=False, quiet=True)

                client.delete_stack(
                    StackName=stack['StackName']
                )


class BaseBuildTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        self.test_path = os.path.join('tests', self._test_name)
        super(BaseBuildTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(BaseBuildTest, self).setUp()
        self.addCleanup(self._clean_build_path)

    @property
    def _test_name(self):
        return self.__class__.__module__.split('.', 1)[0]

    def _test_project_step(self, filename):
        with cd(os.path.join(self.test_path, filename)):
            code = gordon(['gordon', 'build'])
            self.assertEqual(code, 0)

    def _clean_build_path(self):
        build_path = os.path.join(self.test_path, '_build')
        if os.path.exists(build_path):
            shutil.rmtree(build_path)

    def assertBuild(self, step, filename):
        self.assertEqualBuildJsonFiles(
            os.path.join(self.test_path, step, '_build', filename),
            os.path.join(self.test_path, step, '_tests', filename)
        )

    def assertEqualBuildJsonFiles(self, a, b):
        with open(a, 'r') as af, open(b, 'r') as bf:
            a = json.loads(af.read())
            b = json.loads(bf.read())
            template_type = 'custom' if '_type' in a else 'cloudformation'
            if template_type == 'cloudformation':
                # Certain cloudformation resources names need to change from
                # build to build, so we need to make some adjustments before
                # comparing them
                for template in (a, b):
                    new_resources = {}
                    for name, resource in six.iteritems(template.get('Resources', {})):
                        if resource['Type'] == 'AWS::ApiGateway::Deployment':
                            name = name[:-8]
                        new_resources[name] = resource
                    template['Resources'] = new_resources
            self.assertEqual(a, b)

    def assertRun(self, filename, lambda_name, stdin_input, expected_output):
        fake_stdin = tempfile.NamedTemporaryFile(mode='w')
        fake_stdin.write(stdin_input)
        fake_stdin.seek(0)

        with cd(os.path.join(self.test_path, filename)):
            with Capturing() as output:
                code = gordon(['gordon', 'run', lambda_name], stdin=fake_stdin)
            self.assertEqual(output, expected_output)
            self.assertEqual(code, 0)


@attr('integration')
class BaseIntegrationTest(BaseBuildTest):

    def __init__(self, *args, **kwargs):
        super(BaseIntegrationTest, self).__init__(*args, **kwargs)
        self.uid = 'gt{}'.format(hashlib.sha1(six.text_type(uuid.uuid4()).encode('utf-8')).hexdigest()[:5])
        self.test_path = os.path.join('tests', self._test_name)
        self.extra_env = {}

    def setUp(self):
        self.extra_env['CODE_BUCKET_NAME'] = 'gordon-tests-{}'.format(
            hashlib.sha1(six.text_type(random.random()).encode('utf-8')).hexdigest()[:10]
        )

        self._environ = dict(os.environ)
        os.environ.update(self.extra_env)
        self.addCleanup(self._restore_context)
        self.addCleanup(delete_test_stacks, self.uid)
        self.addCleanup(self._clean_extra_env)

    def _test_project_step(self, filename):
        super(BaseIntegrationTest, self)._test_project_step(filename)
        with cd(os.path.join(self.test_path, filename)):
            code = gordon([
                'gordon',
                'apply',
                '--stage={}'.format(self.uid),
            ])
            self.assertEqual(code, 0)

    def _restore_context(self):
        os.environ.clear()
        os.environ.update(self._environ)

    def _clean_extra_env(self):
        self.extra_env = {}

    def assert_stack_succeed(self, stack_name):
        name = generate_stack_name(self.uid, self._test_name, stack_name)
        client = boto3.client('cloudformation')
        stacks = client.describe_stacks(StackName=name)
        self.assertEqual(len(stacks['Stacks']), 1)
        stack = stacks['Stacks'][0]
        self.assertIn(stack['StackStatus'], ('CREATE_COMPLETE',))

    def assert_lambda_response(self, response, value):
        self.assertEqual(json.loads(response['Payload'].read().decode('utf-8')), value)

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

    def get_rule(self, rule_name):
        client = boto3.client('events')
        matches = []
        for f in client.list_rules().get('Rules', []):
            name = f['Name'].split('-')
            if name[0] == self.uid and rule_name.startswith(name[-2]):
                matches.append(f)
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            raise KeyError("Ambiguous rule {}".format(rule_name))
        raise KeyError(rule_name)

    def get_rule_targets(self, rule_name):
        client = boto3.client('events')
        return client.list_targets_by_rule(Rule=rule_name).get('Targets', [])

    def invoke_lambda(self, function_name, payload=None):
        client = boto3.client('lambda')
        return client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            LogType='Tail',
            Payload=json.dumps(payload or {}),
        )

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
