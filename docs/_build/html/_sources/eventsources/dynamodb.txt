Dynamodb
=============

Amazon DynamoDB is a fully managed NoSQL database service that provides fast and predictable performance with seamless scalability.

Gordon allow you to integrate your lambdas with dynamodb using their streams service. DynamoDB Streams captures a time-ordered sequence of
item-level modifications in any DynamoDB table, and stores this information in a log for up to 24 hours.
Applications can access this log and view the data items as they appeared before and after they were modified, in near real time.

Every time one of our dynamodb tables get's modified, dynamo notifies the stream, and one of our lambdas is executed.

.. note::

  As always, is not gordon's business to create the source ``stream``. You should create them in advance. You can read Why in the :doc:`../faq`

.. _dynamodb-anatomy:

Anatomy of the integration
----------------------------------


 .. code-block:: yaml

  dynamodb:

    { INTEGRATION_NAME }:
      lambda: { LAMBDA_NAME }
      stream: { STREAM_ARN }
      batch_size: { BATCH_SIZE }
      starting_position: { STARTING_POSITION }


Batch size
------------

You can pick any number of events from ``1`` to ``10000``. Default value is ``100``.

Starting position
-------------------

You need to pick either:

  * ``TRIM_HORIZON``: Start reading at the last (untrimmed) stream record, which is the oldest record in the shard. In DynamoDB Streams, there is a 24 hour limit on data retention. Stream records whose age exceeds this limit are subject to removal (trimming) from the stream.
  * ``LATEST``: Start reading just after the most recent stream record in the shard, so that you always read the most recent data in the shard.


Full Example
----------------------------------

.. code-block:: yaml

  dynamodb:

    my_dynamodb_integration:

      lambda: app.dynamoconsumer
      stream: arn:aws:dynamodb:eu-west-1:123456789:table/dynamodbexample/stream/2015-11-14T11:18:58.642
      batch_size: 100
      starting_position: LATEST
