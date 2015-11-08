import os
import re
import time
import copy
import json

import boto3
from botocore.exceptions import ClientError
import yaml

from . import exceptions


NEGATIVE_CF_STATUS = (
    'CREATE_FAILED', 'DELETE_FAILED', 'ROLLBACK_FAILED',
    'UPDATE_ROLLBACK_FAILED', 'UPDATE_ROLLBACK_COMPLETE',
    'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS', 'ROLLBACK_COMPLETE'
)

POSITIVE_CF_STATUS = (
    'CREATE_COMPLETE', 'DELETE_COMPLETE', 'UPDATE_COMPLETE',
)

IN_PROGRESS_STATUS = (
    'CREATE_IN_PROGRESS', 'DELETE_IN_PROGRESS', 'ROLLBACK_IN_PROGRESS',
    'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_IN_PROGRESS',
    'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_ROLLBACK_IN_PROGRESS'
)


def load_settings(filename, default=None):
    """Returns a dictionary of the settings included in the YAML file
    called ``filename``. If the file is not present or empty, and empty
    dictionary is used. If ``default`` settings are preovided, those will be
    used as base."""
    settings = copy.copy(default)
    if not os.path.isfile(filename):
        custom_settings =  {}
    else:
        with open(filename, 'r') as f:
            custom_settings = yaml.load(f) or {}
    settings.update(custom_settings)
    return settings


def valid_cloudformation_name(*elements):
    elements = sum([re.split(r'[^a-zA-Z0-9]', e.title()) for e in elements], [])
    return ''.join(elements)

def get_cf_stack(name):
    client = boto3.client('cloudformation')
    try:
        return client.describe_stacks(StackName=name)['Stacks'][0]
    except ClientError, e:
        if e.response['Error']['Code'] == 'ValidationError':
            return None
        raise

def filter_context_for_template(context, template_body):
    template = json.loads(template_body)
    parameters = [[k, v] for k, v in context.iteritems() if k in template['Parameters']]
    return dict(parameters)


def create_stack(name, template_filename, context, **kwargs):
    client = boto3.client('cloudformation')
    with open(template_filename, 'r') as f:
        template_body = f.read()

    parameters = filter_context_for_template(context, template_body)
    stack = client.create_stack(
        StackName=name,
        TemplateBody=template_body,
        Parameters=[{'ParameterKey': k, 'ParameterValue': v} for k, v in parameters.iteritems()],
        TimeoutInMinutes=kwargs.get('TimeoutInMinutes', 25),
        Capabilities=['CAPABILITY_IAM'],
        OnFailure='ROLLBACK'
    )
    return get_cf_stack(stack['StackId'])


def update_stack(name, template_filename, context, **kwargs):
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
            return get_cf_stack(name)
        raise

    return get_cf_stack(stack['StackId'])


def wait_for_cf_status(stack_id, success_if, abort_if, every=1, limit=60 * 15):
    client = boto3.client('cloudformation')
    for i in xrange(0, limit, every):
        stack = get_cf_stack(name=stack_id)
        if stack:
            stack_status = stack['StackStatus']
            if stack_status in success_if:
                return stack
            elif stack_status in abort_if:
                raise exceptions.AbnormalCloudFormationStatusError(
                    stack=stack,
                    success_if=success_if,
                    abort_if=abort_if
                )
        time.sleep(every)


def create_or_update_cf_stack(name, template_filename, context=None, **kwargs):
    context = context or {}
    stack = get_cf_stack(name)

    if stack and stack['StackStatus'] in IN_PROGRESS_STATUS:
        raise exceptions.CloudFormationStackInProgressError()

    if stack:
        print "update stack"
        stack = update_stack(name, template_filename, context=context, **kwargs)
        stack = wait_for_cf_status(stack['StackId'], ('CREATE_COMPLETE',), NEGATIVE_CF_STATUS)
    else:
        print "create stack"
        stack = create_stack(name, template_filename, context=context, **kwargs)
        stack = wait_for_cf_status(stack['StackId'], POSITIVE_CF_STATUS, NEGATIVE_CF_STATUS)

    return stack
