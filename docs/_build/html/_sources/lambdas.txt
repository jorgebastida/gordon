Lambdas
========

Gordon has two aims:
 * Easily deploy and manage lambdas.
 * Easily connect those lambdas to other AWS services (kinesis, dynamo, s3, etc...)

Lambdas are simple functions written in any of the supported AWS languages (python, javascript and java).
If you want to know more, you can read AWS documentation in the topic:

  * `What Is AWS Lambda? <http://docs.aws.amazon.com/lambda/latest/dg/welcome.html>`_
  * `AWS Lambda FAQs <https://aws.amazon.com/lambda/faqs/>`_
  * `AWS Lambda Limits <http://docs.aws.amazon.com/lambda/latest/dg/limits.html>`_

Working with lambdas is quite easy to start with, but once you want to develop
some complex integrations, it becomes a bit of a burden to deal with all the
required steps to put some changes live. Gordon tries to make the entire process
as smooth as possible.

In gordon, Lambdas are resources that you'll group and define within :doc:`apps`. The idea
is to keep Lambdas with the same business domain close to each other in the same app.

.. image:: _static/structure/lambdas.png

Before we continue, there is a bit of terminology we need to make clear:

=====================  ================================================================================================
Term                   Description
=====================  ================================================================================================
``lambda``             Is a static working piece of code ready to be run on AWS.
``lambda version``     Static point-in-time representation of a working lambda.
``lambda alias``       Pointer to a lambda.
``code bucket``        S3 bucket where your lambda code is uploaded.
``code``               S3 Object which contains your lambda code and all required libraries/packages (zip)
``code version``       S3 Object Version of one of your lambda code.
``runtime``            Language in which the lambda code is written (python, javascript or java)
=====================  ================================================================================================

What gordon will do for you?
-----------------------------

* Download any external requirement you lambdas might have.
* Create a zip file with your lambda, packages and libraries.
* Upload this file to S3.
* Create a lambda with your code and settings (memory, timeout...)
* Publish a new version of the lambda.
* Create an alias named ``current`` pointing to this new version.
* Create a new IAM Role for this lambda and attach it.

As result, your lambda will be ready to run on AWS!

.. image:: _static/lambdas.gif

As you can imagine, this is quite a lot of things to do every time you want to simply deploy a new change! That's where gordon tries to help.

With simply two commands, ``build`` and ``apply`` you'll be able to deploy your changes again and again with no effort.


Why the current alias is important?
------------------------------------

The ``current`` alias gordon creates pointing to your most recent lambda is really important.
When gordon creates a new event sources (like S3, Dynamo or Kinesis), it'll make those call the lambda aliased as ``current`` instead of the ``$LATEST``.

This is really important to know, because it enables you to (in case of neccesary) change your ``current`` alias to point to any previous version of the same lambda without
needing to re-configure all related event sources.

Any subsequent deploy to the same stage will point the ``current`` alias to your latest function.

For more information you can read `AWS Lambda Function Versioning and Aliases <http://docs.aws.amazon.com/lambda/latest/dg/versioning-aliases.html>`_.

.. _lambdas-anatomy:

Anatomy of a Lambda
--------------------

The following is the anatomy of a lambda in gordon.

.. code-block:: yaml

  lambdas:

    { LAMBDA_NAME }:
      code: { CODE_PATH }
      handler: { LAMBDA_HANDLER }
      memory: { LAMBDA_MEMORY }
      timeout: { LAMBDA_TIMEOUT }
      runtime: { LAMBDA_RUNTIME }
      description: { LAMBDA_DESCRIPTION }
      role: { LAMBDA_ROLE }
      vpc: { VPC_NAME }
      context: { CONTEXT_NAME }
      auto-vpc-policy: { AUTO_VPC_POLICY }
      auto-run-policy: { AUTO_RUN_POLICY }
      policies:
        { POLICY_NAME }:
          { POLICY_BODY }
        ...

The best way to organize you lambdas is to register them inside the ``settings.yml`` file of your :doc:`apps` within your :doc:`project`.


Lambda Properties
-------------------


name
^^^^^^^^^^^^^^^^^^^^^^

Name for your lambda. Try to keep it as descriptive as possible.

code
^^^^^^^^^^^^^^^^^^^^^^

Path where the code of your lambda is. When creating lambdas you can:

    * Put all the code of your lambda in the same file and point to it:
        * ``code: code.py``
        * ``code: example.js``
    * Create a folder and put several files on it
        * ``code: myfolder``
        * When you point ``code`` to a folder you need to remember to specify the ``runtime`` of your lambda as gordon can't infer it from the filename.


Simple python lambda:

.. code-block:: yaml

    lambdas:
      hello_world:
        code: functions.py


Folder javascript lambda:

.. code-block:: yaml

    lambdas:
      hello_world:
        code: myfolder
        handler: file.handler
        runtime: nodejs4.3


Java lambda:

.. code-block:: yaml

    lambdas:
      hello_world:
        code: myfolder
        handler: example.Hello::handler
        runtime: java8


handler
^^^^^^^^^^^^^^^^^^^^^^

Name of the function within ``code`` which will be the entry point of you lambda.

.. code-block:: yaml

  lambdas:
    hello_world:
      code: functions.py
      handler: my_handler

For the java runtime, this handler will need to have the following format (``package.class::method``):

.. code-block:: yaml

  lambdas:
    hello_world:
      code: helloworld
      runtime: java8
      handler: helloworld.Hello::handler

.. note::

  For more information about Java handlers <http://docs.aws.amazon.com/lambda/latest/dg/java-programming-model-handler-types.html>`_


memory
^^^^^^^^^^^^^^^^^^^^^^

Amount of memory your lambda will get provisioned. This needs to be a multiple of ``64``.
The minimum value is ``128`` and the maximum ``1536``. Default value is ``128``.

.. code-block:: yaml

  lambdas:
    hello_world:
      code: functions.py
      memory: 1536

timeout
^^^^^^^^^^^^^^^^^^^^^^

The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based
on the function's expected execution time. By default, Timeout is set to 3 seconds.

.. code-block:: yaml

  lambdas:
    hello_world:
      code: functions.py
      memory: 300

runtime
^^^^^^^^^^^^^^^^^^^^^^

Runtime of your lambda. Valid values are:

=======================================================  ================
Runtime                                                  AWS Runtime
=======================================================  ================
``node``, ``nodejs``, ``node0.10`` and ``nodejs0.10``    ``nodejs``
``node4.3`` and ``nodejs4.3``                            ``nodejs4.3``
``python`` and ``python2.7``                             ``python2.7``
``java`` and ``java8``                                   ``java8``
=======================================================  ================

If you don't specidy any runtime, Gordon tries to auto detect it based on the extensions of the ``code`` file.

=====================  ===============
Extension              Runtime
=====================  ===============
``.js``                ``nodejs4.3``
``.py``                ``python2.7``
=====================  ===============

For folder based lambdas (like ``java``) the code is a directory and not a file, so the runtime can't be inferred.
For these situations, you can specify the runtime using this setting.


.. code-block:: yaml

    lambdas:
      hello_world:
        code: hellojava
        runtime: java8


description
^^^^^^^^^^^^^^^^^^^^^^

Human-readable description for your lambda.

.. code-block:: yaml

  lambdas:
    hello_world:
      code: functions.py
      description: This is a really simple function which says hello

role
^^^^^^^^^^^^^^^^^^^^^^

ARN of the lambda role this function will use.

If not provided, gordon will create one role for this function for you and include all necessary ``policies`` *(This is the default and most likely behaviour you want).*

.. code-block:: yaml

  lambdas:
    hello_world:
      code: functions.py
      role: arn:aws:iam::account-id:role/role-name

.. _lambdas-vpc:

vpc
^^^^^^^^^^^^

Name of the vpc where this lambda should be deployed. If the Lambda function requires access to resources in a VPC, specify a VPC configuration
that Lambda uses to set up an elastic network interface (ENI). The ENI enables your function to connect to other resources in your VPC, but it doesn't provide
public Internet access.

If your function requires Internet access (for example, to access AWS services that don't have VPC endpoints), configure a Network Address Translation (NAT) instance
inside your VPC or use an Amazon Virtual Private Cloud (Amazon VPC) NAT gateway. For more information, see `NAT Gateways <http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/vpc-nat-gateway.html>`_ in the Amazon VPC User Guide.

.. code-block:: yaml

  lambdas:
    hello_world:
      code: functions.py
      vpc: my-vpc


You need to define some properties about your vpc (in this example ``my-vpc``) in the project settings.

.. code-block:: yaml

    ---
    project: vpcexample
    ...

    vpcs:
        my-vpc:
            security-groups:
                - sg-00000000
            subnet-ids:
                - subnet-1234567a
                - subnet-1234567b
                - subnet-1234567c


If ``auto-vpc-policy`` is ``True``, gordon will attach to your lambda role the required policy which would allow it to access the vpc. It it is ``False``, you'll need
to do this by yourself.

context
^^^^^^^^^^^^

Name of the context you want to inject into this lambda. By default, Gordon will attach the context called ``default`` if it is present.

.. code-block:: yaml

  lambdas:
    hello_world:
      code: functions.py
      context: context_name


policies
^^^^^^^^^^^^^^^^^^^^^^

List of AWS policies to attach to the role of this lambda. This is the way you'll give permissions to you lambda to connect to other AWS services
such as dynamodb, kinesis, s3, etc... For more inforamtion `AWS IAM Policy Reference <http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html>`_

In the following example we attach one policy called ``example_bucket_policy`` to our lambda ``hello_world`` in order to make it possible to read and write a
S3 bucket called ``EXAMPLE-BUCKET-NAME``.

.. code-block:: yaml

  lambdas:
    hello_world:
      code: functions.py
      policies:
        example_bucket_policy:
          Version: "2012-10-17"
          Statement:
            -
              Action:
                - "s3:ListBucket"
                - "s3:GetBucketLocation"
              Resource: "arn:aws:s3:::EXAMPLE-BUCKET-NAME"
              Effect: "Allow"
            -
              Action:
                - "s3:PutObject"
                - "s3:GetObject"
                - "s3:DeleteObject"
                - "dynamodb:GetRecords"
              Resource: "arn:aws:s3:::EXAMPLE-BUCKET-NAME/*"
              Effect: "Allow"


auto-vpc-policy
^^^^^^^^^^^^^^^^^^^
If ``auto-vpc-policy`` is ``True``, and you lambda has one ``vpc`` configured, gordon will attach to your lambda role the required policy which would allow it to
access the vpc. It it is ``False``, you'll need to do this by yourself.

.. code-block:: json

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ec2:CreateNetworkInterface"
                ],
                "Resource": [
                    "*"
                ]
            }
        ]
    }


auto-run-policy
^^^^^^^^^^^^^^^^^^^
If ``auto-run-policy`` is ``True``, gordon will attach to your lambda role the required policy which would allow it to run and push logs.

.. code-block:: json

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "lambda:InvokeFunction"
                ],
                "Resource": [
                    "*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*",
            }
        ]
    }
