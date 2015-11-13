from troposphere import Ref


def ref(value):
    return Ref(value)

BASE_BUILD_PROTOCOLS = {
    'ref': ref,
}

BASE_APPLY_PROTOCOLS = {
    'ref': ref,
    'dynamodb-starswith': ref,
    'dynamodb-endswith': ref,
    'dynamodb-match': ref,
    'kinesis-starswith': ref,
    'kinesis-endswith': ref,
    'kinesis-match': ref,
}
