Advanced Parameters
====================

It is great that you can abstract your project to use different parameters on each stage, but sometimes the fact that those parameters are
static makes quite hard to describe your needs.

There are two ways you can customize your parameters further, Protocols and Templates.

Protocols
-----------

Protocols are helpers which will allows you to make the value of one parameter be dynamic. Protocols are evaluated on ``apply`` time.


Reference ``env://``
^^^^^^^^^^^^^^^^^^^^^

You can make the value of your parameter be based on any environment variable using the ``env://`` protocol.

.. code-block:: yml

    ---
    MyParameter: env://MY_ENV_VARIABLE

gordon will make the parameter ``MyParameter`` value be whatever ``MY_ENV_VARIABLE`` value is on ``apply`` time.


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
