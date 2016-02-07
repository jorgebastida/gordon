Quickstart Java
======================

Now that you have Gordon installed, let's create our first project. Before doing so, you need to understand how Gordon projects are structured.

A Gordon project consist in one or more applications. The term application describes a directory that provides some set of features. Applications may be reused in various projects.

Creating a project
------------------

From the command line, cd into a directory where you’d like to store your code, then run the following command:

.. code-block:: bash

    $ gordon startproject demo

This will create a `demo` directory in your current directory with the following structure:

.. code-block:: bash

    demo
    └── settings.yml

As you can imagine that `settings.yml` file will contain most of our project-wide settings. If you want to know more, :doc:`settings` will tell you how the settings work.

Creating an application
------------------------

Now that we have our project created, we need to create our first app. Run the following command from the command line:

.. code-block:: bash

    $ gordon startapp firstapp --runtime=java

.. note::

    You can create lambdas in any of the AWS supported languages (Python, Javascript and Java) and you can mix them within the same project and app. By default ``startapp`` uses the python runtime, but you can pick a different one by adding ``--runtime=py|javascript`` to it.


This will create a `firstapp` directory inside your project with the following structure:

.. code-block:: bash

    firstapp/
    ├── helloworld
    │   ├── build.gradle
    │   └── src
    │       └── main
    │           └── java
    │               └── helloworld
    │                   └── Hello.java
    └── settings.yml

.. note::

    If you pick ``python`` or ``js`` as runtime, the layout will not be 100% the same, but pretty similar.

These files are:

  * ``helloworld.java`` : File where the source code of our first helloworld lambda will be. By default gordon creates a function called ``handler`` in this file.
  * ``build.gradle`` : Gradle file gordon will use to build your lambda.
  * ``settings.yml`` : Configuration related to this application. By default gordon registers a ``helloworld`` lambda the function within ``Hello.java``.

Once you understand how everything works, and you start developing your app, you'll rename/remove this function, but to start with we think this is the easiest way for you to understand how everything works.

Give it a look to ``firstapp/settings.yml`` and ``firstapp/helloworld/src/main/java/helloworld/Hello.java`` files in order to get a better understanding of what gordon just created for you.

Now that we know what these files does, we need to install this ``firstapp``. In order to do so, open your project ``settings.yml`` and add ``firstapp`` to the ``apps`` list:

.. code-block:: yml

    ---
    project: demo
    default-region: us-east-1
    code-bucket: gordon-demo-5f1fb41f
    apps:
      - gordon.contrib.helpers
      - gordon.contrib.lambdas
      - firstapp

This will make Gordon take count of the resources registered within the ``firstapp`` application.


Build your project
-------------------

Now that your project is ready, you need to build it. You'll need to repeat this step every single time you make some local changes and want to deploy them to AWS.

From the command line, cd into the project root, then run the following command:

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


What is all this? Well, without going into much detail, gordon has just decided that deploying you application implies three stages.
 * ``0001_p.json`` gordon is going to create a s3 bucket where the code of your lambdas will be uploaded.
 * ``0002_pr_r.json`` gordon will upload the code of your lambdas to S3.
 * ``0003_r.json`` gordon will create your lambdas.

But, should I care? **No** you should not really care much about what is going on. The only important part is that you'll now see a new ``_build`` directory in your project path. That directory contains everything gordon needs to put your lambdas live.

If you want to read more about the internals of gordon project, you read more in the :doc:`project` page.


Deploy your project
---------------------

Deploying a project is a as easy as using the ``apply`` command:

.. code-block:: bash

    $ gordon apply


.. note::

    It is important that you make your AWS credential available in your terminal before, so gordon can use them. For more information: :doc:`setup_aws`

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
      ✓ code/firstapp_helloworld.zip (c7ec05a8)
    0003_r.json (cloudformation)
      CREATE_COMPLETE

Your lambdas are ready to be used!

What next?
-----------

You should have a basic understanding of how Gordon works. We recommend you to dig a bit deeper and explore:

  * :doc:`project` Details about how you can customize your projects
  * :doc:`apps` Internals about how applications work.
  * :doc:`lambdas` In-depth exmplanation of how lambdas work.
  * :doc:`eventsources` List of all resources and integrations you can create using Gordon.
