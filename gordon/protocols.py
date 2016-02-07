import os
import re
import boto3
from troposphere import Ref
from gordon import exceptions


def ref(value):
    return Ref(value)


def env(value):
    return os.environ[value]


def kinesis_match(value):
    exp = re.compile(value)
    client = boto3.client('kinesis')
    paginator = client.get_paginator('list_streams')
    response_iterator = paginator.paginate()
    matches = []
    for response in response_iterator:
        for name in response.get('StreamNames', []):
            if exp.search(name):
                matches.append(name)
    if not matches:
        raise exceptions.ProtocolNotFoundlError("Not found Error: No kinesis stream matches {}".format(value))
    elif len(matches) > 1:
        raise exceptions.ProtocolMultipleMatcheslError(
            "Multiple Matches Error: Several kinesis streams matches {} ({}).".format(value, ','.join(matches))
        )
    return matches[0]


def kinesis_startswith(value):
    return kinesis_match(r'^{}'.format(value))


def kinesis_endswith(value):
    return kinesis_match(r'{}$'.format(value))


def dynamodb_match(value):
    exp = re.compile(value)
    client = boto3.client('dynamodb')
    paginator = client.get_paginator('list_tables')
    response_iterator = paginator.paginate()
    matches = []
    for response in response_iterator:
        for name in response.get('TableNames', []):
            if exp.search(name):
                matches.append(name)
    if not matches:
        raise exceptions.ProtocolNotFoundlError("Not Found Error: No dynamodb table matches {}".format(value))
    elif len(matches) > 1:
        raise exceptions.ProtocolMultipleMatcheslError(
            "Multiple Matches Error: Several dynamodb tables matches {} ({}).".format(value, ','.join(matches))
        )
    return matches[0]


def dynamodb_startswith(value):
    return dynamodb_match(r'^{}'.format(value))


def dynamodb_endswith(value):
    return dynamodb_match(r'{}$'.format(value))


def dynamodb_stream_match(value):
    exp = re.compile(value)
    client = boto3.client('dynamodbstreams')
    matches = []
    for stream in client.list_streams().get('Streams', []):
        if exp.search(stream['TableName']):
            matches.append(stream['StreamArn'])
    if not matches:
        raise exceptions.ProtocolNotFoundlError("Not found Error: No dynamodb stream matches {}".format(value))
    elif len(matches) > 1:
        raise exceptions.ProtocolMultipleMatcheslError(
            "Multiple Matches Error: Several dynamodb stream matches {} ({}).".format(value, ','.join(matches))
        )
    return matches[0]


def dynamodb_stream_startswith(value):
    return dynamodb_stream_match(r'^{}'.format(value))


def dynamodb_stream_endswith(value):
    return dynamodb_stream_match(r'{}$'.format(value))


BASE_BUILD_PROTOCOLS = {
    'ref': ref,
}

BASE_APPLY_PROTOCOLS = {
    'env': env,
    'dynamodb-startswith': dynamodb_startswith,
    'dynamodb-endswith': dynamodb_endswith,
    'dynamodb-match': dynamodb_match,
    'dynamodb-stream-startswith': dynamodb_stream_startswith,
    'dynamodb-stream-endswith': dynamodb_stream_endswith,
    'dynamodb-stream-match': dynamodb_stream_match,
    'kinesis-startswith': kinesis_startswith,
    'kinesis-endswith': kinesis_endswith,
    'kinesis-match': kinesis_match,
}
