Kinesis
=============

Amazon Kinesis Streams enables you to build custom applications that process or analyze streaming data for specialized needs.
Amazon Kinesis Streams can continuously capture and store terabytes of data per hour from hundreds of thousands of sources such as website clickstreams,
financial transactions, social media feeds, IT logs, and location-tracking events.
Kinesis Streams captures a time-ordered sequence of events, and stores this information in a log for up to 7 days.

Gordon allow you to integrate your lambdas with kinesis using their streams service.
Every time on event gets published into the kinesis stream, one of our lambdas is executed.

.. note::

  As always, is not gordon's business to create the source ``stream``. You should create them in advance. :doc:`../why_gordon_dont_create_other_resources`


Anatomy of the integration
---------------------------


 .. code-block:: yaml

  kinesis:

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

  * ``TRIM_HORIZON``: Start reading at the last (untrimmed) stream record, which is the oldest record in the shard. Stream records whose age exceeds 7 days are subject to removal (trimming) from the stream.
  * ``LATEST``: Start reading just after the most recent stream record in the shard, so that you always read the most recent data in the shard.


Full Example
----------------------------------

.. code-block:: yaml

  dynamodb:

    my_kinesis_integration:

      lambda: app.dynamoconsumer
      stream: arn:aws:kinesis:eu-west-1:123456789:stream/kinesisexample
      batch_size: 100
      starting_position: LATEST
