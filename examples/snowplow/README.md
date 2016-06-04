Snowplow Example

This simple project defines one lambda called ``snowplowconsumer`` and integrates it with one kinesis stream.

Items in the stream are expected to be realtime events published by [Snowplow Analytics](http://snowplowanalytics.com/) If you want
to quickly test this example, you can populate an Empty Kinesis stream using ``misc/create_snowplow_events.py YOUR-KINESIS-STREAM 100`` will create
``100`` snowplow events in the kinesis stream named ``YOUR-KINESIS-STREAM``.

Every time changes are published to the stream, the lambda will be executed. The lambda will read those events, process them and using
the [Snowplow Analytics Python SDK](https://github.com/snowplow/snowplow-python-analytics-sdk) and do a simple update in a dynamodb table.

Documentation relevant to this example:
 * [Lambdas](https://gordon.readthedocs.io/en/latest/lambdas.html)
 * [Kinesis](https://gordon.readthedocs.io/en/latest/eventsources/kinesis.html)

How to deploy it?
------------------

* Create a dynamodb table, and add the name to ``DynamodbTable`` in ``parameters/dev.yml``
* Create a Kinesis stream and get the ARN by running:
 * ``$ aws kinesis describe-stream --stream-name NAME``
* Add the arn to ``KinesisIntegrationArn`` in ``parameters/dev.yml``
* ``$ gordon build``
* ``$ gordon apply``
* Send a test message to your kinesis by doing:
 * ``$ misc/create_snowplow_events.py YOUR-KINESIS-STREAM 100``
