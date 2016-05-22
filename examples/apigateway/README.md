Apigateway Example
===========================

![gordon](http://gordondoc.s3-website-eu-west-1.amazonaws.com/_static/examples/apigateway.svg)

This simple project defines one API Gateway called ``helloapi``and connects two
lambdas: one written in python called ``helloapi`` and one written in javascript
called ``hellojs``.

These two lambdas are defined within an application called ``helloworld``.

This apigateway defines several resources (urls). Some of them are quite simple, but some
other are quite more advanced like ``/404``, ``/http``, ``/mock`` and ``/complex/implementation``.

Documentation relevant to this example:
 * [Lambdas](http://gordondoc.s3-website-eu-west-1.amazonaws.com/lambdas.html)
 * [APIGateway](http://gordondoc.s3-website-eu-west-1.amazonaws.com/eventsources/apigateway.html)

How to deploy it?
------------------

* ``$ gordon build``
* ``$ gordon apply``

You should get an output similar to:

```shell
Applying project...
  0001_p.json (cloudformation)
    CREATE_COMPLETE
  0002_pr_r.json (custom)
    ✓ code/contrib_lambdas_version.zip (6f256866)
    ✓ code/helloworld_hellojs.zip (b56d8430)
    ✓ code/helloworld_hellopy.zip (5cecbbbc)
  0003_r.json (cloudformation)
    CREATE_COMPLETE
Project Outputs:
  LambdaHelloworldHellopy
    arn:aws:lambda:us-east-1:xxxxxxxxx:function:dev-apigateway-r-HelloworldHellopy-10DWZF3J5LXW9:current
  LambdaHelloworldHellojs
    arn:aws:lambda:us-east-1:xxxxxxxxx:function:dev-apigateway-r-HelloworldHellojs-1OS6KNIZZIY5J:current
  ApigatewayHelloapi
    https://xxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev
```
