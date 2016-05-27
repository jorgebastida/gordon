Kinesis Example
===========================

![gordon](http://gordondoc.s3-website-eu-west-1.amazonaws.com/_static/examples/kinesis.svg)

This simple project defines one lambda called ``kinesisconsumer`` and integrates it with one kinesis stream.

Every time 10 changes are published to the stream, the lambda will be executed.

The lambda is quite dumb, and only prints the received event.


Documentation relevant to this example:
 * [Lambdas](http://gordondoc.s3-website-eu-west-1.amazonaws.com/lambdas.html)
 * [Kinesis](http://gordondoc.s3-website-eu-west-1.amazonaws.com/eventsources/kinesis.html)

How to deploy it?
------------------

* Create a Kinesis stream and get the ARN by running:
 * ``$ aws kinesis describe-stream --stream-name NAME``
* ``$ gordon build``
* ``$ gordon apply``
* Send a test message to your kinesis by doing:
 * ``$ aws kinesis put-record --stream-name gordon-test  --partition-key 123 --data hello``
