Advanced Parameters
====================

It is great that you can abstract your project to use different parameters on each stage, but sometimes the fact that those parameters are
static makes quite hard to describe your needs.

There are two ways you can customize your parameters further, Protocols and Templates.

Protocols
-----------

Protocols are helpers which will allows you to make the value of one parameter be dynamic. Protocols are evaluated on ``apply`` time.


Environment Variables
^^^^^^^^^^^^^^^^^^^^^^^

You can make the value of your parameter be based on any environment variable using the ``env://`` protocol.

.. code-block:: yml

    ---
    MyParameter: env://MY_ENV_VARIABLE

gordon will make the parameter ``MyParameter`` value be whatever ``MY_ENV_VARIABLE`` value is on ``apply`` time.

Dynamodb
^^^^^^^^^^^

You can dynamically lookup for dynamodb tables which name starts with, ends with or matches certain text.

===========================  ============================================================
Name                         Description
===========================  ============================================================
``dynamodb-startswith://``   Table name startswith certain text
``dynamodb-endswith://``     Table name ends with certain text
``dynamodb-match://``        Table name match certain regular expression
===========================  ============================================================

Example:

.. code-block:: yml

    ---
    MyParameter: dynamodb-startswith://clients-

gordon will make the parameter ``MyParameter`` value be the full name of the table which name starts with ``clients-``.

If several (or none) dynamodb tables match any of these criterias, gordon will fail before trying to apply this project.


Dynamodb Streams
^^^^^^^^^^^^^^^^^^

You can dynamically lookup for dynamodb streams which table name starts with, ends with or matches certain text.

==================================  ============================================================
Name                                Description
==================================  ============================================================
``dynamodb-stream-startswith://``   Table name startswith certain text
``dynamodb-stream-endswith://``     Table name ends with certain text
``dynamodb-stream-match://``        Table name match certain regular expression
==================================  ============================================================

Example:

.. code-block:: yml

    ---
    MyParameter: dynamodb-stream-startswith://clients-

gordon will make the parameter ``MyParameter`` value be the ``ARN`` of the stream of which table name starts with ``clients-``.

If several (or none) dynamodb tables match any of these criterias, gordon will fail before trying to apply this project.


Kinesis
^^^^^^^^^^^

You can dynamically lookup for kinesis streams which name starts with, ends with or matches certain text.

===========================  ============================================================
Name                         Description
===========================  ============================================================
``kinesis-startswith://``    Kinesis stream name startswith certain text
``kinesis-endswith://``      Kinesis stream name ends with certain text
``kinesis-match://``         Kinesis stream name match certain regular expression
===========================  ============================================================

Example:

.. code-block:: yml

    ---
    MyParameter: kinesis-startswith://events-

gordon will make the parameter ``MyParameter`` value be the full name of the table which name starts with ``events-``.

If several (or none) kinesis streams match any of these criterias, gordon will fail before trying to apply this project.


Jinja2 Templates
------------------

If you want to customize your parameter values even further, you can use jinja2 syntax to customize the value of your parameters.

The context gordon will provide to this jinja helper is:

 * ``stage``: The name of the stage where you are applying your project.
 * ``aws_region``: The name of the AWS_REGION where you are applying your project.
 * ``aws_account_id``: The ID of the account that you are using to apply your project.
 * ``env``: All available environment variables.


Example:

.. code-block:: yml

    ---
    MyBucket: "company-{{ stage }}-images"


There are lot's of things you can do with Jinja2. For more information `Jinja2 Template Designer Documentation <http://jinja.pocoo.org/docs/dev/templates/#filters>`_
