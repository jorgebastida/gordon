S3 Example
===========================

![gordon](http://gordondoc.s3-website-eu-west-1.amazonaws.com/_static/examples/s3.svg)

This simple project defines one lambda called ``s3consumer``, and integrates it with a s3 bucket.

Every time a ``s3:ObjectCreated:*`` or ``s3:ObjectRemoved:*`` event is triggered in the
bucket (when objects are created or removed), our lambda ``s3consumer`` will be invoked.

The lambda itself is quite dumb, and only prints the received event.

Documentation relevant to this example:
 * [Lambdas](http://gordondoc.s3-website-eu-west-1.amazonaws.com/lambdas.html)
 * [S3](http://gordondoc.s3-website-eu-west-1.amazonaws.com/eventsources/s3.html)

How to deploy it?
------------------

* ``$ gordon build``
* ``$ gordon apply``
