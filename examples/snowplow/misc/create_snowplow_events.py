import sys
import random

import boto3
from snowplow_analytics_sdk.event_transformer import ENRICHED_EVENT_FIELD_TYPES


def create_fake_event(**kwargs):
    print kwargs
    data = []
    for k, _ in ENRICHED_EVENT_FIELD_TYPES:
        data.append(kwargs.get(k, ''))
    return '\t'.join(data)


def main(stream, total):
    client = boto3.client('kinesis')
    for i in xrange(total):

        event = create_fake_event(
            se_category=['impression', 'engagement'][random.randint(0, 1)],
            se_value=str(random.randint(1, 5)),
            se_label=str(random.randint(1, 10))
        )

        client.put_record(
            StreamName=stream,
            Data=event,
            PartitionKey='shardId-000000000000',
        )

if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))
