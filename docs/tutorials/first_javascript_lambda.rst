My first Javascript Lambda
============================

In this example we are going to create our first javascript lambda using gordon. This lambda is going to do the same than the ``Hello World`` example AWS provides as blueprint. This
is:

 * Receive an input message
 * Log ``key1``, ``key2`` and ``key3`` values.
 * Return ``key1`` as result.

The test message we'll use to test this function is the following:

.. code-block:: json

  {
    "key3": "value3",
    "key2": "value2",
    "key1": "value1"
  }

Before we start, make sure you have:

 * An AWS Account
 * You've setup your AWS credentials in your machine (:doc:`../setup_aws`)
 * Gordon is installed (:doc:`../installation`)

Create your Project
--------------------

From the command line, cd into a directory where you’d like to store your code, then run the following command:

.. code-block:: bash

    $ gordon startproject hellojs

This will create a `hellojs` directory in your current directory with the following structure:

.. code-block:: bash

    hellojs
    └── settings.yml

This is the minimal layout of a project. We are now going to create an application.

Create your Application
------------------------

Run the following command from the command line:

.. code-block:: bash

    $ gordon startapp firstapp --runtime=js

This will create a `firstapp` directory inside your project with the following structure:

.. code-block:: bash

    firstapp/
    ├── helloworld.js
    └── settings.yml

By default, when you create a new application, gordon will create one really simple lambda called ``helloworld``.

In the next step we'll install your application

Install your application
------------------------

In order to install your application you need to add it to the ``apps`` list in the project ``settings.yml``.

Edit your project ``settings.yml`` file and add ``firstapp`` to the list of installed apps.

.. code-block:: yaml

  ---
  project: hellojs
  default-region: us-east-1
  apps:
    - gordon.contrib.helpers
    - gordon.contrib.lambdas
    - firstapp

In the next step we are going to make the default lambda gordon provides, do what we want it to do.

Create your Lambda
--------------------

Open you ``firstapp/helloworld.js`` file and edit it until it looks to something like this:

.. code-block:: javascript

  exports.handler = function(event, context) {
    console.log('value1 =', event.key1);
    console.log('value2 =', event.key2);
    console.log('value3 =', event.key3);
    context.succeed(event.key1);  // Echo back the first key value
  };

The code of our lambda is ready! We only need to double check it is correctly registered.

Open your ``firstapp/settings.yml``. It should look similar to this:

.. code-block:: yaml

  lambdas:
    helloworld:
      code: helloworld.js
      #description: Simple functions in js which says hello
      #handler: handler
      #role:
      #memory:

This file is simply registering a lambda called ``helloworld``, and telling gordon the source of the lambda is in ``helloworld.js`` file.

The default behaviour for gordon is to assume the function to call in your source file is called ``handler``. You can change this behaviour by changing the ``handler`` section
in your lambda settings.

Now we are ready to build your project!

Build your project
--------------------

In the root of your project run the following command

.. code-block:: bash

    $ gordon build

This command will have an output similar to:

.. code-block:: bash

    $ gordon build
    Loading project resources
    Loading installed applications
      contrib_helpers:
        ✓ sleep
      contrib_lambdas:
        ✓ alias
        ✓ version
      firstapp:
        ✓ helloworld
    Building project...
      ✓ 0001_p.json
      ✓ 0002_pr_r.json
      ✓ 0003_r.json

If that's the case... great! Your project is ready to be deployed.

Deploy your project
--------------------

Projects are deployed by calling the command ``apply``. Apply will assume by default you want to deploy your project
into a new stage called ``dev``.

Stages are 100% isolated deployments of the same project. The idea is that the same project
can be deployed in the same AWS account in different stages (``dev``, ``staging``, ``production``...) in order to SAFELY test your lambda behaviour.

If you don't provive any stage using ``--stage=STAGE_NAME`` a default stage called ``dev`` will be used.

Once you are ready, call the following command:

.. code-block:: bash

    $ gordon apply

This command will have an output similar to:

.. code-block:: bash

    $ gordon apply
    Applying project...
      0001_p.json (cloudformation)
        CREATE_COMPLETE waiting... -
      0002_pr_r.json (custom)
        ✓ code/contrib_helpers_sleep.zip (364c5f6d)
        ✓ code/contrib_lambdas_alias.zip (e906090e)
        ✓ code/contrib_lambdas_version.zip (c3137e97)
        ✓ code/firstapp_helloworld.zip (db6f502e)
      0003_r.json (cloudformation)
        CREATE_COMPLETE

And you are done! Your lambda is ready to be used on AWS!

Test your Lambda
--------------------

In order to test it, you can navigate into your `Lambda Console <https://console.aws.amazon.com/lambda/home?#/functions>`_ and:

  * Click on the lambda we have just created. It should be called something like: ``dev-hellojs-r-FirstappHelloworld-XXXXXXXX``
  * Click the blue button named ``Test``
  * Select the ``Hello World`` Sample event template (It should come selected by default)
  * Click ``Save and Test``
  * You should get a succeed message: ``Execution result: succeeded``, and some log information.


Congratulations! You've just deployed your first lambda into AWS using gordon!
