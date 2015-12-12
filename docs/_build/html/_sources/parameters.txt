Parameters
=============

Parameters are the artifact around the fact that project templates (what gordon generates into ``_build``) should be immutable between stages.
Parameters allow you to have specific stage settings.

How can I user parameters?
---------------------------

In order to use parameters you only need to:
 * Create a directory called ``parameters``
 * Inside of this directory, create ``.yml`` files for your different stages (``dev.yml``, ``prod.yml``, ...)
 * Replace values in your settings with ``ref://MyParameter``
 * Add values for ``MyParameter`` in ``dev.yml``, ``prod.yml`` ...

.. note::

   You can create a file called ``common.yml``, and place all shared parameters between stages on it. When this file is present, gordon will read it first, and then
   update the parameters map using your stage-specific settings file (if pressent).

If you want to customize your parameters further, read :doc:`parameters_advanced`, where you'll find information on how make paramater values be dynamic.


Example
--------

Let's imagine you wan to call one lambda every time a file is created in one of your buckets.

 * First, you'll create and register a lambda
 * then you'll create a new s3 integration which connects ``my-production-bucket`` with ``app.mys3consumer`` when a ``s3:ObjectCreated:*`` happens.

Something like this:

.. code-block:: yaml

  s3:
    my_s3_integration:
      bucket: my-production-bucket
      notifications:

        - id: lambda_on_create_cat
          lambda: app.mys3consumer
          events:
            - s3:ObjectCreated:*

This is good to start with, but what about if once this is working great for a while... you want to test how a new lambda function works? You'll probably need to:

 * Change the bucket name to a test one ``my-production-bucket`` -> ``my-dev-bucket``
 * Build your project ``gordon build``
 * Apply the project into a test stage ``gordon apply --stage=test``
 * Test your lambda
 * If everything is ok, remember to change the name of the buckets back to the original, and deploy it to production again.

This is tedious and unmaintainable.

Solution
---------

The solution is as simple as making your bucket name be a parameter. In this case we are calling the parameter ``MyS3IntegrationBucket``.

.. code-block:: yaml

  s3:
    my_s3_integration:
      bucket: ref://MyS3IntegrationBucket
      notifications:

        - id: lambda_on_create_cat
          lambda: app.mys3consumer
          events:
            - s3:ObjectCreated:*

Then, in the root of you project, create a new directory called ``parameters`` and create a new file with the name of each of the stages (``dev`` and ``prod``).

.. code-block:: bash

    ...
    parameters/
    ├── prod.yml
    └── dev.yml

Then, we can define two different values for ``MyS3IntegrationBucket`` based on the stage where we are applying the project.

``prod.yml`` will have the production bucket:

.. code-block:: yaml

  ---
  MyS3IntegrationBucket: my-production-bucket


and ``dev.yml`` will have the dev one:

.. code-block:: yaml

  ---
  MyS3IntegrationBucket: my-dev-bucket


Now we can simply run:

 * ``gordon apply --stage=dev``
 * ``gordon apply --stage=prod``

And the correct settings will be used.

How it works?
--------------

When you define in your settings file a value as a reference ``ref://``, gordon will automatically register (on ``build`` time) all required input parameters in your CloudFormation templates
and collect  values from your parameters files when you call ``apply``.
