Gordon Apigateway Example
===========================

![gordon](http://gordondoc.s3-website-eu-west-1.amazonaws.com/_static/examples/apigateway.svg)

This simple project defines one API Gateway called ``helloapi``and connects two
lambdas: one written in python called ``helloapi`` and one written in javascript
called ``hellojs``.

These two lambdas are defined within an application called ``helloworld``.

This apigateway defines several resources. Some of them are quite simple, but some
other are quite more advanced like ``/404``, ``/http``, ``/mock`` and ``/complex/implementation``.

The documentation relevant to this example is:
 * [Lambdas](http://gordondoc.s3-website-eu-west-1.amazonaws.com/lambdas.html)
 * [APIGateway](http://gordondoc.s3-website-eu-west-1.amazonaws.com/eventsources/apigateway.html)
