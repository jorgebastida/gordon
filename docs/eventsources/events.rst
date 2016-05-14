Events
========================

Amazon CloudWatch Events delivers a near real-time stream of system events that describe changes in Amazon Web Services (AWS) resources to AWS Lambda functions as well as
trigger events on a pre-determined schedule .

Using simple rules that you can quickly set up, you can match events and route them to one or more target functions.

A full list of available events can be found here: http://docs.aws.amazon.com/AmazonCloudWatch/latest/DeveloperGuide/EventTypes.html

.. _events-anatomy:

Anatomy of the integration
----------------------------------

.. code-block:: yaml

  events:

    { INTEGRATION_NAME }:
      state: { STATE }
      description: { DESCRIPTION }
      schedule_expression: { RATE }
      event_pattern: { PATTERN }
      targets:
        { TARGET_ID }:
          lambda: { LAMBDA_NAME }
          input: { INPUT }
          input_path: { INPUT_PATH }


.. note::

    You need to specify either ``schedule_expression``, ``event_pattern`` or both.


State
-------------------

You need to pick between:

    * ``ENABLED``: Your lambda will be scheduled.
    * ``DISABLED``: Your lambda will not be scheduled.


Schedule Expression
---------------------

All scheduled events use UTC time zone and the minimum precision for schedules is 1 minute. CloudWatch Events supports the following formats:

    * ``cron(<Fields>)``
    * ``rate(<Value> <Unit>)``

For more information about ``cron`` and ``rate``: http://docs.aws.amazon.com/AmazonCloudWatch/latest/DeveloperGuide/ScheduledEvents.html

Examples:

    * ``cron(0 10 * * ? *)`` Run at 10:00 am (UTC) every day.
    * ``cron(0 18 ? * MON-FRI *)`` Run at 06:00 pm (UTC) every Monday through Friday.
    * ``cron(0/15 * * * ? *)`` Run every 15 minutes.
    * ``rate(5 minutes)`` Every 5 minutes.
    * ``rate(1 hour)`` Every 1 hour.
    * ``rate(2 day)`` Every 2 day.


Event pattern
----------------

Rules use event patterns to select events and route them to targets. A pattern either matches an event or it doesn't.
Event patterns are represented as objects with a structure that is similar to that of events.

.. code-block:: yaml

  event_pattern:
      source:
          - aws.ec2
      detail:
          state:
              - pending

For more information about Events: http://docs.aws.amazon.com/AmazonCloudWatch/latest/DeveloperGuide/CloudWatchEventsandEventPatterns.html

Targets
--------

Map of target lambdas to connect this event to, as well as optional input and input_path information.

.. code-block:: yaml

  targets:
    say_hello:
      lambda: helloworld.hellopy

  say_hello:
    lambda: helloworld.hellopy
    input: xxx
    input_path: yyy

Full Example
----------------------------------

.. code-block:: yaml

  events:
    every_night:
      schedule_expression: cron(0 0 * * ? *)
      description: Call example_lambda every midnight.
      state: ENABLED

      targets:
        say_hello:
          lambda: helloworld.hellopy  # Example lambda

    new_asg_instance:
      description: Do something when an autoscaling-group instance-launch happens
      state: ENABLED

      targets:
        say_hello:
          lambda: helloworld.hellopy  # Example lambda

      event_pattern:
          source:
              - aws.autoscaling
          detail:
              LifecycleTransition:
                - autoscaling:EC2_INSTANCE_LAUNCHING
