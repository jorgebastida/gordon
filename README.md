![gordon](http://gordondoc.s3-website-eu-west-1.amazonaws.com/_static/logo_text.svg)

[![GitHub license](https://img.shields.io/badge/license-BSD-blue.svg)](COPYING)
![Python Versions](https://img.shields.io/badge/python-2.7%20%7C%203.3%20%7C%203.4%20%7C%203.5-green.svg)
![Beta](https://img.shields.io/badge/status-beta-orange.svg)
[![PyPI version](https://badge.fury.io/py/gordon.svg)](https://pypi.python.org/pypi/gordon/)
[![Travis Build](https://api.travis-ci.org/jorgebastida/gordon.svg?branch=master)](https://travis-ci.org/jorgebastida/gordon)


Gordon is a tool to create, wire and deploy AWS Lambdas using CloudFormation

Documentation: http://gordon.readthedocs.io/en/latest/

Features
---------
* 100% CloudFormation resource creation
* 100% Boilerplate free
* 100% isolated and dead-simple multi-stage and multi region deployments
* Python/Javascript/Java/Golang/... runtimes supported.
* Run Lambdas locally (Python/Javascript/Java/Golang/...)
* Simple yml configuration
* Seamless integration with (``pip``,``npm``, ``gradle``, ...)
* 100% Customizable lambda build process. Use ``Docker``, ``Makefile`` or... a simple ``shell`` script.

* Supported integrations
  * APIGateway  
  * Scheduled CloudWatch Events (cron)
  * CloudWatch Events
  * Dynamodb Streams
  * Kinesis Streams
  * S3
* AWS Lambda Versions an Aliases
* VPC support
* Dynamic stage parametrization including:
  * Environment variables
  * Jinja2 values
  * ARN translation helpers
* Extensive Documentation
* Good test suite
* Love ❤️


Example Projects
------------------

We think documentation and examples are an important pilar... so here you have a nice list of things you can play with!

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
* [Slack Bot](https://github.com/jorgebastida/gordon/tree/master/examples/slack): Create a simple slash command bot for Slack.
* [Twilio](https://github.com/jorgebastida/gordon/tree/master/examples/twilio): Integrate your lambdas with Twilio using TwiML.
* [Snowplow Analytics](https://github.com/jorgebastida/gordon/tree/master/examples/snowplow): Consume Snowplow Analytics events from gordon.
* [Docker](https://github.com/jorgebastida/gordon/tree/master/examples/docker): Compile lambdas with native dependencies within a docker container thanks to [lambci/docker-lambda](https://github.com/lambci/docker-lambda)


Why should you use this project?
-----------------------------------

Because this project doesn't introduces anything new. Gordon is just a thin layer of sugar around AWS services and few conventions, which makes deploying and wiring Lambdas really easy.

Under the hood, gordon just generates self-contained CloudFormation templates... which is great!

Why introduce yet-another framework when you can build lambdas using AWS services and tools you already know how to use (``pip``, ``npm``, ``grunt``, ``gulp``, ``gradle``, ``Makefile``...)

Keep it simple! 😀


Isolation between stages?
-----------------------------------

Yes, we believe that there must be 100% isolation between your application stages (``dev``, ``staging``, ``prod``...). That means that resources which (for example) serve a development purpose **must** not be related to the ones which are serving production load. Putting that to the extreme, [and following AWS best practices](http://blogs.aws.amazon.com/security/post/TxQYSWLSAPYVGT/Guidelines-for-when-to-use-Accounts-Users-and-Groups) that means using different AWS accounts. This completely clash with the suggested approach that AWS suggest you to follow with services such as apigateway, where they emphasize to have several "stages" for the same apigateway resource. We disagree and completely ignore that functionality.

Gordon keeps reproducibility and isolation at it's core. When you apply gordon projects in different stages or regions, you'll deploy completely isolated Cloudformation stacks which will contain an exact and isolated copy of all the resources you have defined.


Why CloudFormation?
-----------------------
One of the best advantages of using AWS is the fact that reproducibility is at it's core and their ecosystem is full of services which encourage it. Their flagship is CloudFormation.

Then... why not just use CloudFormation? Well, there are three reasons:

1. **Complexity**: CloudFormation stacks are defined using JSON templates which are a nightmare to write and maintain. And remember... *Friends don't let friends write JSON files*.
2. **Glue**: There is a lot of glue to put in between a "normal user" and the reality-check of deploying and wiring a Lambda into AWS.
3. **APIs**: Not all AWS APIs are released when services are announced... ain't frameworks (boto3), nor integrations with CloudFormation.

This project tries to solve these three issues by:

1. Creating a really thin layer of conventions on top of easy to maintain YAML files.
2. Making everything work out of the box as well trying to make people not shoot in their foot.
3. Working around the lack of CloudFormation/Framework APIs (keeping in mind they will eventually happen).


Does gordon use gordon to deploy gordon?
-----------------------------------------
Yes, we eat our own dog food; We use gordon to create gordon. The idea is that, (unlike many other projects) we don't think streaming API commands to AWS is a nice solution, so instead, we fill the gaps with custom CloudFormation resources.

Those Custom CloudFormation resources are implemented using Lambdas (deployed by gordon)... crazy uh?!

Why all this madness? Again... because reproducibility. If you manage some resources using CloudFormation, and some others streaming API commands, if/when you try to reproduce or decommission your environment... you are pretty much f\*\*\*.

Feedback
-----------

We would love to hear as much feedback as possible! If you have any comment, please drop me an email to me@jorgebastida.com
