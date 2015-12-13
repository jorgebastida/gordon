Lambdas
========

Gordon has two aims:
 * Create and deploy lambdas
 * Easily connect those lambdas to other AWS services (kinesis, dynamo, s3, etc...)

They are the most basic element we'll create . Lambdas are simple functions
written in any of the supported AWS languages (python, javascript and java)
which we'll upload to AWS and then connect with several other services.

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
``code version``       S3 Object Version of one of your lambda codes.
``runtime``            Language in which the lambda code is written (python, javascript or java)
=====================  ================================================================================================


In short, every time you want to deploy your lambdas into AWS gordon will:

* Create a zip file with your code, packages and libraries.
* Upload this file to S3 as new version of the same Object.
* Modify the lambda code to point to the new package
* Make any other required changes to the lambda (memory, etc..)
* Create  a new version of the lambda
* Move the ``current`` alias to this new version

.. image:: _static/lambdas.gif


As you can imagine, this is quite a lot of things to do every time you want to simply upload
a new piece of code! That's where gordon tries to help.


Anatomy of a Lambda
============================


.. code-block:: yaml

  lambdas:

    { LAMBDA_NAME }:
      code: { CODE_FILENAME }
      handler: { LAMBDA_HANDLER }
      memory: { LAMBDA_MEMORY }
      timeout: { LAMBDA_TIMEOUT }
      description: { LAMBDA_DESCRIPTION }
      update_current_alias: { UPDATE_CURRENT_ALIAS }
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


update_current_alias
^^^^^^^^^^^^^^^^^^^^^^

Toggle if any subsequent ``apply`` should update the ``current`` alias of this function to the latest one. Valid values are (``true`` and ``false``).
Default value is ``true``.

.. code-block:: yaml

  lambdas:
    hello_world:
      code: functions.py
      update_current_alias: false

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

ARN of the lambda role this function will use. If not provided, gordon will create one role for this function and include all necessary ``policies``.
This is the default behaviour.

.. code-block:: yaml

  lambdas:
    hello_world:
      code: functions.py
      role: arn:aws:iam::account-id:role/role-name

policies
^^^^^^^^^^^^^^^^^^^^^^

List of AWS policies to attach to the role of this lambda. This is the way you'll make it possible to you lambda to connect to other AWS services
such as dynamodb, kinesis, s3, etc..

In the following example we attach one policy to our lambda ``hello_world`` in order to make it possible to read a dynamodb stream.

.. code-block:: yaml

  lambdas:
    hello_world:
      code: functions.py
      policies:
        read_dynamodb:
          Version: "2012-10-17"
          Statement:
            -
              Action:
                - "dynamodb:DescribeStream"
                - "dynamodb:ListStreams"
                - "dynamodb:GetShardIterator"
                - "dynamodb:GetRecords"
              Resource: "arn:aws:dynamodb:*:*:*"
              Effect: "Allow"
