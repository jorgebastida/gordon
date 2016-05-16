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
      stream: { ARN }
      batch_size: { INT }
      starting_position: { STARTING_POSITION }


Properties
-------------------


Integration Name
^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         Key of the ``dynamodb`` map.
Required                     Yes
Valid types                  ``string``
Max length                   30
Description                  Name for your dynamodb integration. Try to keep it as short and descriptive as possible.
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
Description                  Arn of the dynamodb stream you want to connect your lambda with.
===========================  ============================================================================================================


Batch size
^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         ``stream``
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


* TRIM_HORIZON: Start reading at the last (untrimmed) stream record, which is the oldest record in the shard. In DynamoDB Streams, there is a 24 hour limit on data retention. Stream records whose age exceeds this limit are subject to removal (trimming) from the stream.
* LATEST: Start reading just after the most recent stream record in the shard, so that you always read the most recent data in the shard.


Full Example
----------------------------------

.. code-block:: yaml

  dynamodb:

    my_dynamodb_integration:

      lambda: app.dynamoconsumer
      stream: arn:aws:dynamodb:eu-west-1:123456789:table/dynamodbexample/stream/2015-11-14T11:18:58.642
      batch_size: 100
      starting_position: LATEST
