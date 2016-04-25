Contexts
============

Contexts in Gordon are groups of variables which you want to make accessible to your code, but
you don't want to hardcode into it because it's values are dependant on the the deployment.

This could be for example because ``dev`` and ``production`` lambdas (although beeing the same code), need to connect to
different resources, use different passwords or produce slightly different outputs.

In the same way, same lambdas deployed to different regions will probably need to connect to different places.

Contexts solve this problem by injecting a small payload into the lambdas package on deploy time, and letting
you read that file on run time using your language of choice.


How contexts works
---------------------

The first thing you'll need to do is define a context in your project settings file (``project/settings.yml``).

.. code-block:: yaml

  ---
  project: my-project
  default-region: eu-west-1
  code-bucket: my-bucket
  apps:
    ...
  contexts:
    default:
      database_host: 10.0.0.1
      database_username: dev-bob
      database_password: shrug
  ...

As you can see, we have defined a context called ``default``. All lambdas by default inject the context called ``default`` if it is present.

After doing this, Gordon will leave a ``.context`` JSON file at the root of your lambda package. You can use your language of choice to read and use it.

In the following example, we use python to read this file.

.. code-block:: python

    import json
    print('Loading function')

    with open('.context', 'r') as f:
        context = json.loads(f.read())

    def handler(event, context):
        return context['database_host']  # Echo the database host

Advanced contexts
-------------------------

For obvious reasons, hardcoding context values in your ``project/settings.yml`` file is quite limited and not very flexible. For this reason Gordon allows you to
make the value of any of the context variables reference any parameter.

In the following example, we are going to make all three variables point to three respective parameters. This will allow us to change the value of the context variables
easily between stages or regions.

.. code-block:: yaml

  ---
  project: my-project
  default-region: eu-west-1
  code-bucket: my-bucket
  apps:
    ...
  contexts:
    default:
      database_host: ref://DatabaseHost
      database_username: ref://DatabaseUsername
      database_password: ref://DatabasePassword
  ...

Now we only need to define what is the value for each of these parameters creating (for example) a ``parameters/common.yml`` file

.. code-block:: yaml

  ---
  DatabaseHost: 10.0.0.1
  DatabaseUsername: "{{ stage }}-bob"
  DatabasePassword: env://MY_DATABASE_PASSWORD


As you can see this is quite a fancy example, because values are now dynamically generated.

=====================  =================================================================================================================================================
Parameter              Value
=====================  =================================================================================================================================================
``DatabaseHost``       This is a fixed hardcoded value ``10.0.0.1``.
``DatabaseUsername``   This is a jinja2 parameter. If we apply our project into a stage called ``prod`` it's value will be ``prod-bob``
``DatabasePassword``   This parameter will have as value whatever the ``MY_DATABASE_PASSWORD`` env variable has when you apply your project.
=====================  =================================================================================================================================================


Now you should have a basic understanding of how contexts works. If you want to learn more about ``parameters`` you'll find all the information you need in:

  * :doc:`parameters` How parameters works
  * :doc:`parameters_advanced` Advanced usages of parameters.
