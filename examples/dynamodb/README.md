Dynamodb Example
===========================

![gordon](http://gordon.readthedocs.io/en/latest/_static/examples/dynamodb.svg)

This simple project defines one lambda called ``dynamoconsumer`` and integrates it with one dynamodb stream.

Every time 10 changes are published to the stream, the lambda will be executed.

The lambda is quite dumb, and only prints the received event.

Documentation relevant to this example:
 * [Lambdas](http://gordon.readthedocs.io/en/latest/lambdas.html)
 * [Dynamodb](http://gordon.readthedocs.io/en/latest/eventsources/dynamodb.html)

How to deploy it?
------------------

* ``$ gordon build``
* ``$ gordon apply``
