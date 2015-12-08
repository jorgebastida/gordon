import os

from troposphere import Ref


def ref(value):
    return Ref(value)

def env(value):
    return os.environ[value]


BASE_BUILD_PROTOCOLS = {
    'ref': ref,
}

BASE_APPLY_PROTOCOLS = {
    'ref': ref,
    'env': env,
    'dynamodb-starswith': ref,
    'dynamodb-endswith': ref,
    'dynamodb-match': ref,
    'kinesis-starswith': ref,
    'kinesis-endswith': ref,
    'kinesis-match': ref,
}
