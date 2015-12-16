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

Before we continue there is a bit of terminology we need to make clear:

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

As result, your lambda will be up and running on AWS!

.. image:: _static/lambdas.gif

As you can imagine, this is quite a lot of things to do every time you want to simply deploy a new change! That's where gordon tries to help.

With simply two commands, ``build`` and ``apply`` you'll be able to deploy your changes again and again with no effort.


Why the current alias is important?
------------------------------------

The ``Current`` alias gordon creates pointing to your most recent lambda is really important.
When gordon creates a new event sources (like S3, Dynamo or Kinesis), it'll make those call the lambda aliased as ``Current`` instead of the ``$LATEST``.

This is really important to know, because it enables you to (in case of neccesary) change your ``Current`` alias to point any previous version of the same lambda without
needing to re-configure all related event sources.

Any subsequent deploy to the same stage will point the ``Current`` alias to your latest function.

For more information you can read `AWS Lambda Function Versioning and Aliases <http://docs.aws.amazon.com/lambda/latest/dg/versioning-aliases.html>`_.


Anatomy of a Lambda
--------------------

The following is the anatomy of a lambda in gordon.

.. code-block:: yaml

  lambdas:

    { LAMBDA_NAME }:
      code: { CODE_FILENAME }
      handler: { LAMBDA_HANDLER }
      memory: { LAMBDA_MEMORY }
      timeout: { LAMBDA_TIMEOUT }
      description: { LAMBDA_DESCRIPTION }
      python_requirements:
        - { PYTHON_REQUIREMENT_1 }
        - ...
      node_requirements:
        - { NODE_REQUIREMENT_1 }
        - ...
      role: { LAMBDA_ROLE }
      policies:
        { POLICY_NAME }:
          { POLICY_BODY }
        ...

The best way to organize you lambdas is to register them inside the ``settings.yml`` file of your :doc:`apps` within your :doc:`project`.

.. image:: _static/structure/lambdas.png


Lambda Properties
-------------------


name
^^^^^^^^^^^^^^^^^^^^^^

Name for your lambda. Try to keep it as descriptive as possible.

code
^^^^^^^^^^^^^^^^^^^^^^

Filename where the code of your lambda is.

.. code-block:: yaml

  lambdas:
    hello_world:
      code: functions.py

handler
^^^^^^^^^^^^^^^^^^^^^^

Name of the function within ``code`` which will be the entry point of you lambda.

.. code-block:: yaml

  lambdas:
    hello_world:
      code: functions.py
      handler: my_handler

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


description
^^^^^^^^^^^^^^^^^^^^^^

Human-readable description for your lambda.

.. code-block:: yaml

  lambdas:
    hello_world:
      code: functions.py
      description: This is a really simple function which says hello

python_requirements
^^^^^^^^^^^^^^^^^^^^^^

List of `PyPi <https://pypi.python.org/pypi>`_ packages this function requires. You can specify specific versions of your packages
using `PIP <https://pip.pypa.io/en/stable/>`_ syntax. gordon uses ``pip`` under the hood to download your required packages.

.. code-block:: yaml

  lambdas:
    hello_world:
      code: functions.py
      python_requirements:
        - requests
        - python-dateutil==2.4.2
        - lxml>=3.4

node_requirements
^^^^^^^^^^^^^^^^^^^^^^

List of `npm <https://www.npmjs.com/>`_ packages this function requires. You can specify specific versions of your packages
using `npm <https://www.npmjs.com/>`_ syntax. gordon uses ``npm`` under the hood to download your required packages.

.. code-block:: yaml

  lambdas:
    hello_world:
      code: functions.js
      node_requirements:
        - less
        - bower>=1.7

role
^^^^^^^^^^^^^^^^^^^^^^

ARN of the lambda role this function will use.

If not provided, gordon will create one role for this function for you and include all necessary ``policies`` *(This is the default and most likely behaviour you want).*

.. code-block:: yaml

  lambdas:
    hello_world:
      code: functions.py
      role: arn:aws:iam::account-id:role/role-name

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
