Cron
========================

CloudWatch Events allows you to take actions on a pre-determined schedule.

Gordon allow you to wire this functionality with your lambdas and schedule them using cron-like syntax.


.. _cron-anatomy:

Anatomy of the integration
----------------------------------

 .. code-block:: yaml

  cron:

    { INTEGRATION_NAME }:
      lambda: { LAMBDA_NAME }
      expression: { SCHEDULE_EXPRESSION }
      state: { STATE }
      description: { DESCRIPTION }

Schedule Expression
---------------------

All scheduled events use UTC time zone and the minimum precision for schedules is 5 minutes. CloudWatch Events supports the following formats:

    * ``cron(<Fields>)``
    * ``rate(<Value> <Unit>)``

For more information about ``cron`` and ``rate``: http://docs.aws.amazon.com/AmazonCloudWatch/latest/DeveloperGuide/ScheduledEvents.html


Cron Expressions Examples
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    * ``cron(0 10 * * ? *)`` Run at 10:00 am (UTC) every day.
    * ``cron(0 18 ? * MON-FRI *)`` Run at 06:00 pm (UTC) every Monday through Friday.
    * ``cron(0/15 * * * ? *)`` Run every 15 minutes.

Rate Expressions Examples
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    * ``rate(5 minutes)`` Every 5 minutes.
    * ``rate(1 hour)`` Every 1 hour.
    * ``rate(2 day)`` Every 2 day.


State
-------------------

You need to pick either:

  * ``ENABLED``: Your lambda will be scheduled.
  * ``DISABLED``: Your lambda will not be scheduled.


Full Example
----------------------------------

.. code-block:: yaml

  cron:

    every_night:
      lambda: app.example_lambda
      expression: cron(0 0 * * ? *)
      state: ENABLED
      description: Call example_lambda every midnight.
