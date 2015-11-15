Gordon
=========

Gordon is a high-level framework to create, wire and deploy AWS Lambdas in an easy way.

Usage
------
```shell
$ gordon startproject demo [--region=eu-west-1|...]
$ cd demo
$ gordon startapp helloworld [--runtime=py|js]
# ... Add helloword to demo/settings.yml installed apps.
$ gordon build
$ gordon apply [--stage=dev|prod|...]
```


Why?
------
In an ideal world, this project should not exits. AWS Lambdas (as any other AWS resource) should be provisioned using CloudFormation - One of the best advantages of using AWS (imho) is not it's scalability nor the fancy services... ain't the price; It is the fact that reproducibility is at it's core and their ecosystem is full of services which encourage/enforce it. Their flagship is CloudFormation.

Then... why not use CloudFormation? Well, there are two reasons: First, not all AWS APIs are released when services are announced... ain't frameworks (boto3), nor integrations with CloudFormation.

The second reason is complexity. CloudFormation stacks are defined using JSON templates which are a nightmare to write and maintain.

This project tries to solve these two issues by working around the lack of CloudFormation/Framework APIs (keeping in mind they will happen eventually) and trying to create a high level abstraction on top of CloudFormation so people without a deep understanding of it can write and deploy lambdas without shooting their foot.

Features
---------
* 100% CloudFormation resource creation.
* Python/Javascript/Java runtimes supported.
* Simple yml configuration
* Seamless integration with package managers (``pip``,``npm``)
* AWS Lambda Versioning
* AWS Lambda Alias
* Dead-simple custom multi-stage and multi region deployments ``--stage=prod``
* S3 Versioning
* Supported integrations
  * Kinesis Streams
  * Dynamodb Streams
* Dynamic stage parametrization including:
  * jinja2 love
  * Environment variables
  * ARN translation helpers (``dynamodb-starswith://clients-``, ``dynamodb-endswith://-clients``, ``dynamodb-match://clients-`` ...)
* Love

Why should you use this project?
-----------------------------------
Because eventually you'll stop using it -ish. Once CloudFormation supports 100% of the AWS Lambda API, this project will be a really thin layer of sugar around the fact that writing CloudFormation templates sucks and some conventions around how to structure a project using Lambdas... and not much more, which is great!


How it works
-------------
It is easy - we want as much as possible to happen on CloudFormation, so every single thing which could be done with it... will be done with it.

If you are interested in the details, I would recommend you to read ``gordon/contrib/cloudFormation/settings.yml``. That's where all the pain is.

Yes, we eat our own dog food; We use gordon to create gordon. The idea is that, (unlike many other projects), we don't think streaming API commands to AWS is a nice solution to leverage the gaps in the CloudFormation API, so instead, we fill the gaps with custom CloudFormation resources which look like how AWS will implement them -ish ;)

Those Custom CloudFormation resources are implemented using Lambdas (deployed by gordon)... crazy uh?!

Why all this madness? Again... because reproducibility. If you manage some resources using CloudFormation, and some others streaming API commands, when you try to decommission your environment... you are pretty much f***, and you MUST use the original tool to (hopefully) delete all resources. With Gordon this is not a problem. You delete our CloudFormation stacks and all our sh** is gone.
