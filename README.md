![gordon](http://gordondoc.s3-website-eu-west-1.amazonaws.com/_static/logo_text.svg)

[![GitHub license](https://img.shields.io/badge/license-BSD-blue.svg)](COPYING)

Gordon is a tool to create, wire and deploy AWS Lambdas using CloudFormation in an easy way.

Documentation: http://gordondoc.s3-website-eu-west-1.amazonaws.com/

Features
---------
* 100% CloudFormation resource creation.
* 100% Boilerplate free
* Python/Javascript/Java/Golang runtimes supported.
* Simple yml configuration
* Seamless integration with (``pip``,``npm``, ``gradle`` ...)
* Dead-simple custom multi-stage and multi region deployments ``--stage=prod``
* Supported integrations
  * APIGateway  
  * CloudWatch Events (cron)
  * Dynamodb Streams
  * Kinesis Streams
  * S3
* AWS Lambda Versions an Aliases
* Dynamic stage parametrization including:
  * Environment variables
  * Jinja2 values
  * ARN translation helpers
* Extensive Documentation
* Good test suite
* Love


Example Projects
------------------
* [Python HelloWorld Lambda](https://github.com/jorgebastida/gordon/tree/master/examples/modulepython): Simple Lambda written in Python.
* [Javascript HelloWorld Lambda](https://github.com/jorgebastida/gordon/tree/master/examples/modulejs): Simple Lambda written in Javascript.
* [Javascript ES6 HelloWorld Lambda](https://github.com/jorgebastida/gordon/tree/master/examples/simplejs-es6): Simple Lambda written in Javascript using ES-6.
* [Java HelloWorld Lambda](https://github.com/jorgebastida/gordon/tree/master/examples/simplejava): Simple Lambda written in Java.
* [Golang Runtime](https://github.com/jorgebastida/gordon/tree/master/examples/go): Run Golang based Lambdas via shim.
* [ApiGateway](https://github.com/jorgebastida/gordon/tree/master/examples/apigateway): Integration for creating a simple web service.
* [Cron](https://github.com/jorgebastida/gordon/tree/master/examples/cron): Schedule lambdas using cron syntax.
* [Dynamodb Stream Consumer](https://github.com/jorgebastida/gordon/tree/master/examples/dynamodbpython): Consume as a stream changes to a dynamodb table.
* [Kinesis Stream Consumer](https://github.com/jorgebastida/gordon/tree/master/examples/kinesispython): Consume Events published in a Kinesis Stream.
* [S3 Consumer](https://github.com/jorgebastida/gordon/tree/master/examples/s3): Run your lambdas when a file is created/deleted on S3.
* [Contexts](https://github.com/jorgebastida/gordon/tree/master/examples/contexts): Add dynamic configuration to your lambdas.
* [Lambda based Custom CloudFormation Resouces](https://github.com/jorgebastida/gordon/tree/master/examples/cloudformation-custom-resources): Manage CloudFormation resources using Lambdas.
* [Telegram Bot](https://github.com/jorgebastida/gordon/tree/master/examples/telegram): Create a simple bot in telegram.
* [Twilio](https://github.com/jorgebastida/gordon/tree/master/examples/twilio): Integrate your lambdas with Twilio using TwiML.
* [Snowplow Analytics](https://github.com/jorgebastida/gordon/tree/master/examples/snowplow): Consume Snowplow Analytics events from gordon.


Why should you use this project?
-----------------------------------

Because this project doesn't introduces anything new. Gordon is a thin layer of sugar around the fact that writing CloudFormation templates by hand is a nightmare and some conventions around how to structure a project using Lambdas... and not much more, which is great!

Why introduce yet-another framework when you can build lambdas using tools you already know (``pip``, ``npm``, ``grunt``, ``gulp``, ``gradle``, ``Makefile``...) and deploy them using a service Amazon cares about and maintains?

Keep it simple! 😀


Why CloudFormation?
-----------------------
One of the best advantages of using AWS is the fact that reproducibility is at it's core and their ecosystem is full of services which encourage it. Their flagship is CloudFormation.

Then... why not use only CloudFormation? Well, there are three reasons:

1. **Complexity**: CloudFormation stacks are defined using JSON templates which are a nightmare to write and maintain. And remember, Friends don't let friends write JSON files.
2. **Glue**: There is a lot of glue to put in between a "normal user" and the reality-check of deploying and wiring a Lambda into AWS.
3. **APIs**: Not all AWS APIs are released when services are announced... ain't frameworks (boto3), nor integrations with CloudFormation.

This project tries to solve these three issues by:

1. Creating a really thin layer of conventions on top of easy to maintain YAML files.
2. Making everything work out of the box as well trying to make people not shoot in their foot.
3. Working around the lack of CloudFormation/Framework APIs (keeping in mind they will eventually happen).


Does gordon use gordon to deploy gordon?
-----------------------------------------
Yes, we eat our own dog food; We use gordon to create gordon. The idea is that, (unlike many other projects), we don't think streaming API commands to AWS is a nice solution, so instead, we fill the gaps with custom CloudFormation resources.

Those Custom CloudFormation resources are implemented using Lambdas (deployed by gordon)... crazy uh?!

Why all this madness? Again... because reproducibility. If you manage some resources using CloudFormation, and some others streaming API commands, if/when you try to reproduce or decommission your environment... you are pretty much f\*\*\*.
