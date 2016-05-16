Kinesis
=============

Amazon Kinesis Streams enables you to build custom applications that process or analyze streaming data for specialized needs.
Amazon Kinesis Streams can continuously capture and store terabytes of data per hour from hundreds of thousands of sources such as website clickstreams,
financial transactions, social media feeds, IT logs, and location-tracking events.
Kinesis Streams captures a time-ordered sequence of events, and stores this information in a log for up to 7 days.

Gordon allow you to integrate your lambdas with kinesis using their streams service.
Every time on event gets published into the kinesis stream, one of our lambdas is executed.

.. note::

  As always, is not gordon's business to create the source ``stream``. You should create them in advance. You can read Why in the :doc:`../faq`

.. _kinesis-anatomy:


Anatomy of the integration
---------------------------


 .. code-block:: yaml

  kinesis:

    { INTEGRATION_NAME }:
      lambda: { LAMBDA_NAME }
      stream: { ARN }
      batch_size: { INT }
      starting_position: { STARTING_POSITION }


Properties
-------------------


Integration Name
^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         Key of the ``kinesis`` map.
Required                     Yes
Valid types                  ``string``
Max length                   30
Description                  Name for your kinesis integration. Try to keep it as short and descriptive as possible.
===========================  ============================================================================================================

Lambda
^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         ``lambda``
Required                     Yes
Valid types                  ``lambda-name``
Description                  Name of the lambda you want to notify
===========================  ============================================================================================================


Stream
^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         ``stream``
Required                     Yes
Valid types                  ``arn``
Description                  Arn of the kinesis stream you want to connect your lambda with.
===========================  ============================================================================================================


Batch size
^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         ``batch_size``
Required                     No
Default                      100
Valid types                  ``integer``
Min                          1
Max                          10000
Description                  Number of events you want your lambda to receive at once
===========================  ============================================================================================================


Starting position
^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         ``starting_position``
Required                     Yes
Valid Values                  ``TRIM_HORIZON``, ``LATEST``
Description                  Number of events you want your lambda to receive at once
===========================  ============================================================================================================


* TRIM_HORIZON: Start reading at the last (untrimmed) stream record, which is the oldest record in the shard.
* LATEST: Start reading just after the most recent stream record in the shard, so that you always read the most recent data in the shard.



Full Example
----------------------------------

.. code-block:: yaml

  kinesis:

    my_kinesis_integration:

      lambda: app.kinesisconsumer
      stream: arn:aws:kinesis:eu-west-1:123456789:stream/kinesisexample
      batch_size: 100
      starting_position: LATEST
