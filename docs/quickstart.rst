Quickstart
============

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

    $ gordon startapp firstapp

.. note::

    You can create lambdas in any of the AWS supported languages (Python, Javascript and Java) and you can mix them within the same project and app. By default ``startapp`` uses the python runtime, but you can pick a different one by adding ``--runtime=js|java`` to it.


This will create a `firstapp` directory inside your project with the following structure:

.. code-block:: bash

    firstapp/
    ├── lambdas.py
    └── settings.yml

.. note::

    If you pick ``java`` o ``js`` as runtime, the layout will not be 100% the same, but pretty similar.

These files are:

  * ``lambdas.py`` : File where the source code of your lambdas will be. By default gordon creates a function called ``handler`` in this file.
  * ``settings.py`` : Configuration related to this application. By default gordon registers as ``helloworld`` the function within ``lambdas.py``.

Once you understand how everything works, and you start developing your app, you'll rename/remove this function, but to start with we think this is the easiest way for you to understand how everything works.

Give it a look to ``firstapp/settings.yml`` and ``firstapp/lambdas.py`` files in order to get a better understanding of what gordon just created for you.

Now that we know what these files does, we need to install this ``firstapp``. In order to do so, open your project ``settings.yml`` and add ``firstapp`` to the ``apps`` list:

.. code-block:: yml

    ---
    project: demo
    default-region: us-east-1
    apps:
      - gordon.contrib.cloudformation
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
      cloudformation:
        ✓ lambda_alias
        ✓ sleep
        ✓ lambda_version
      firstapp:
        ✓ helloworld
    Building project...
      ✓ 0001_project.json
      ✓ 0002_pre_resources.json
      ✓ 0003_resources.json


What is all this? ...

What next?
-----------

You should have a basic understanding of how Gordon works. We recommend you to dig a bit deeper and explore:

  * :doc:`project` Details about how you can customize your projects
  * :doc:`apps` Internals about how applications work.
  * :doc:`resources` List of all resources and integrations you can create using Gordon.
