Cron Example
===========================

![gordon](https://gordon.readthedocs.io/en/latest/_static/examples/cron.svg)

This simple project defines one lambda called ``hellopy``, and two CloudWatch rules called
``every_night`` and ``update_dns``.

* ``every_night`` is triggered every day at midnight.
* ``update_dns`` is triggered every three minutes if an EC2 instance has entered the ``pending`` state.

The lambda is quite dumb, and only prints the received event.

Documentation relevant to this example:
 * [Lambdas](https://gordon.readthedocs.io/en/latest/lambdas.html)
 * [Events](https://gordon.readthedocs.io/en/latest/eventsources/events.html)

How to deploy it?
------------------

* ``$ gordon build``
* ``$ gordon apply``
