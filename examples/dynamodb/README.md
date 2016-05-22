Gordon Dynamodb Example
===========================

![gordon](http://gordondoc.s3-website-eu-west-1.amazonaws.com/_static/examples/dynamodb.svg)

This simple project defines one lambda called ``dynamoconsumer`` and integrates it with one dynamodb stream.

Every time 10 changes are published to the stream, the lambda will be executed.

The lambda is quite dumb, and only prints the received event.

Documentation relevant to this example:
 * [Lambdas](http://gordondoc.s3-website-eu-west-1.amazonaws.com/lambdas.html)
 * [Dynamodb](http://gordondoc.s3-website-eu-west-1.amazonaws.com/eventsources/dynamodb.html)

How to deploy it?
------------------

* ``$ gordon build``
* ``$ gordon apply``
