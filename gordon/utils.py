# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import copy
import json
import hashlib
import zipfile

import boto3
from botocore.exceptions import ClientError
import yaml
import jinja2
import troposphere
from troposphere import cloudformation, Join, Ref
from clint.textui import colored, puts, progress, indent

from . import exceptions
from gordon import get_version


FINAL_STATUS = (
    'CREATE_FAILED', 'DELETE_FAILED', 'ROLLBACK_FAILED',
    'UPDATE_ROLLBACK_FAILED', 'UPDATE_ROLLBACK_COMPLETE', 'CREATE_COMPLETE',
    'DELETE_COMPLETE', 'UPDATE_COMPLETE',
    'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS', 'ROLLBACK_COMPLETE',
    'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS'
)


IN_PROGRESS_STATUS = (
    'CREATE_IN_PROGRESS', 'DELETE_IN_PROGRESS', 'ROLLBACK_IN_PROGRESS',
    'UPDATE_IN_PROGRESS', 'UPDATE_ROLLBACK_IN_PROGRESS'
)

DELETE_STACK_STATUS = (
    'CREATE_FAILED', 'DELETE_FAILED', 'ROLLBACK_FAILED',
    'UPDATE_ROLLBACK_FAILED'
)

STATUS_COLORS = {
    'CREATE_FAILED'
}

MILL_CHARS = ['|', '/', '-', '\\']


def get_cf_color(status):
    if 'IN_PROGRESS' in status:
        return colored.yellow
    elif 'ROLLBACK' in status or 'FAILED' in status:
        return colored.red
    return colored.green


def mill(iterable):
    for i, elem in enumerate(iterable):
        yield MILL_CHARS[i % len(MILL_CHARS)], elem


def split_arn(arn):
    match = re.match(r'arn\:aws\:(.+)\:(.+):(\d+):(.+)', value)
    if not match:
        raise exceptions.ResourceValidationError(
            "{} is a don't a valid arn.".format(arn)
        )
    return match.groups()


def get_zip_metadata(filename, metadata_filename='.metadata'):
    """Return metadata information attached to a zip file."""
    zfile = zipfile.ZipFile(filename)
    try:
        return json.loads(zfile.read(metadata_filename))
    except Exception:
        return {}


def file_hash(filename):
    """Return a consistent sha1 hash of a file."""
    with open(filename, 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()


def tree_hash(path):
    """Return a consistent sha1 hash of a directory."""
    digest = hashlib.sha1()
    for root, dirs, files in os.walk(path):
        relative = os.path.relpath(root, path)
        for filename in sorted(files):
            digest.update(os.path.join(relative, filename))
            with open(os.path.join(root, filename), 'rb') as f:
                digest.update(f.read())
    return digest.hexdigest()


def setup_region(region, settings=None):
    """Returns which region should be used and sets ``AWS_DEFAULT_REGION`` in
    order to configure ``boto3``."""
    region = region or os.environ.get('AWS_DEFAULT_REGION', None) or (settings and settings.get('default-region', None)) or 'us-east-1'
    os.environ['AWS_DEFAULT_REGION'] = region
    return region


def load_settings(filename, default=None, jinja2_enrich=False, context=None, protocols=None, ):
    """Returns a dictionary of the settings included in the YAML file
    called ``filename``. If the file is not present or empty, and empty
    dictionary is used. If ``default`` settings are preovided, those will be
    used as base.
    If ``jinja2_enrich``, enrich settings values using jinja2.
    If ``protocols`` enrich settings using those enrichent protocols.
    """

    context = context or {}
    protocols = protocols or []
    settings = copy.copy(default or {})

    if not os.path.isfile(filename):
        custom_settings =  {}
    else:
        with open(filename, 'r') as f:
            custom_settings = yaml.load(f) or {}

    def _jinja2_enrich(obj):
        if isinstance(obj, dict):
            return dict((k, _jinja2_enrich(v)) for k, v in obj.iteritems())
        elif hasattr(obj, '__iter__'):
            return [_jinja2_enrich(v) for v in obj]
        elif isinstance(obj, basestring):
            return jinja2.Template(obj).render(**context)
        return obj

    if jinja2_enrich:
        custom_settings = _jinja2_enrich(custom_settings)

    def _protocol_enrich(obj):
        if isinstance(obj, dict):
            return dict((k, _protocol_enrich(v)) for k, v in obj.iteritems())
        elif hasattr(obj, '__iter__'):
            return [_protocol_enrich(v) for v in obj]
        elif isinstance(obj, basestring):
            match = re.match(r'^(\w+)\:\/\/(.*)$', obj)
            if match:
                protocol, value = match.groups()
                if protocol in protocols:
                    return protocols[protocol](value)
                else:
                    raise exceptions.UnknownProtocolError(protocol, value)
        return obj

    if protocols:
        custom_settings = _protocol_enrich(custom_settings)

    settings.update(custom_settings)
    return settings


def fix_troposphere_references(template):
    """"Tranverse the troposphere ``template`` looking missing references.
    Fix them by adding a new parameter for those references."""

    def _fix_references(obj, template):
        for prop, value in obj.properties.iteritems():
            if isinstance(value, troposphere.Ref):
                name = value.data['Ref']
                if name not in (template.parameters.keys() + template.resources.keys()) and not name.startswith('AWS::'):
                    template.add_parameter(
                        troposphere.Parameter(
                            name,
                            Type="String",
                        )
                    )
            elif isinstance(value, troposphere.BaseAWSObject):
                _fix_references(value, template)

    for _, resource in template.resources.iteritems():
        _fix_references(resource, template)

    return template


def lambda_friendly_name_to_grn(name, alias='current'):
    return 'lambda:{}:{}'.format(name.replace('.', ':'), alias)


def generate_stack_name(stage, project_name, step):
    return '-'.join([stage, project_name, step])


def valid_cloudformation_name(*elements):
    """Generete a valid CloudFormation name using ``elements``
    Because Resource names in AWS are truncaded, we try to respect up to 7
    characters per group, except for the last one, which hopefully is the
    most representative one
    """
    last = len(elements) - 1
    elements = sum([re.split(r'[^a-zA-Z0-9]', e.title()) for e in elements], [])
    #elements = [e[:(6 if i != last else None)] for i, e in enumerate(elements)]
    return ''.join(elements)

def get_cf_stack(name):
    """Returns the CloudFormation stack with name ``name``. If it doesn't exit
    returns None."""
    client = boto3.client('cloudformation')
    try:
        return client.describe_stacks(StackName=name)['Stacks'][0]
    except ClientError, e:
        if e.response['Error']['Code'] == 'ValidationError':
            return None
        raise

def filter_context_for_template(context, template_body):
    """Extracts all required parameter of ``template_body`` from ``context``."""
    template = json.loads(template_body)
    parameters = [[k, v] for k, v in context.iteritems() if k in template['Parameters']]
    return dict(parameters)


def create_stack(name, template_filename, context, timeout_in_minutes, **kwargs):
    """Creates a new CloudFormation stack with name ``name`` using as template
    ``template_filename`` and ``context`` as parameters."""

    client = boto3.client('cloudformation')
    with open(template_filename, 'r') as f:
        template_body = f.read()

    parameters = filter_context_for_template(context, template_body)
    stack = client.create_stack(
        StackName=name,
        TemplateBody=template_body,
        Parameters=[{'ParameterKey': k, 'ParameterValue': v} for k, v in parameters.iteritems()],
        TimeoutInMinutes=timeout_in_minutes,
        Capabilities=['CAPABILITY_IAM'],
        #OnFailure='ROLLBACK'
        OnFailure='DO_NOTHING',
        Tags=[
        {
            'Key': 'GordonVersion',
            'Value': get_version()
        },
    ]
    )
    return get_cf_stack(stack['StackId'])


def update_stack(name, template_filename, context, **kwargs):
    """Updates the stack ``name`` using ``template_filename`` as template and
    ``context`` as parameters"""

    client = boto3.client('cloudformation')
    with open(template_filename, 'r') as f:
        template_body = f.read()

    parameters = filter_context_for_template(context, template_body)
    try:
        stack = client.update_stack(
            StackName=name,
            TemplateBody=template_body,
            Parameters=[{'ParameterKey': k, 'ParameterValue': v} for k, v in parameters.iteritems()],
            Capabilities=['CAPABILITY_IAM'],
        )
    except ClientError, e:
        if e.response['Error']['Message'] == 'No updates are to be performed.':
            puts(colored.green('✓ No updates are to be performed.'))
            return get_cf_stack(name)
        raise

    return get_cf_stack(stack['StackId'])


def wait_for_cf_status(stack_id, success_if, abort_if=None, every=1, limit=60 * 15):
    """Waits up to ``limit`` seconds in ``every`` intervals until the stack
    with ID ``stack_id`` reached one of the status in ``success_if`` or
    ``abort_if``.
    """
    abort_if = abort_if or DELETE_STACK_STATUS
    client = boto3.client('cloudformation')
    clean_output = False
    for m, i in mill(xrange(0, limit, every)):
        stack = get_cf_stack(name=stack_id)
        if stack:
            stack_status = stack['StackStatus']
            if i:
                puts("\r{}".format(" " * 80), newline=False)
                puts("\r    {} waiting... {}".format(get_cf_color(stack_status)(stack_status), m), newline=False)
                sys.stdout.flush()

            if stack_status in success_if:
                if clean_output:
                    puts("")
                return stack
            elif stack_status in abort_if:
                raise exceptions.AbnormalCloudFormationStatusError(stack, stack_status, success_if, abort_if)
            clean_output = True
        time.sleep(every)
    puts("")


def create_or_update_cf_stack(name, template_filename, context=None, **kwargs):
    """Creates or updates the stack called ``name`` using ``template_filename``
    as template and ``context`` as parameters."""
    context = context or {}
    stack = get_cf_stack(name)

    if stack and stack['StackStatus'] in IN_PROGRESS_STATUS:
        raise exceptions.CloudFormationStackInProgressError(stack['StackId'], stack['StackStatus'])

    if stack:
        stack = update_stack(name, template_filename, context=context, **kwargs)
    else:
        stack = create_stack(name, template_filename, context=context, **kwargs)

    stack = wait_for_cf_status(stack['StackId'], FINAL_STATUS)

    return stack


class BaseLambdaAWSCustomObject(cloudformation.AWSCustomObject):
    """Base troposphere Custom Resource implemented using a lambda function
    called ``cf_lambda_name``."""

    @classmethod
    def create_with(cls, *args, **kwargs):
        lambda_arn = kwargs.pop('lambda_arn')
        kwargs['ServiceToken'] = lambda_arn
        return cls(*args, **kwargs)


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, new_path):
        self.new_path = os.path.expanduser(new_path)

    def __enter__(self):
        self.old_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.old_path)
