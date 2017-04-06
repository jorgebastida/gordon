Settings
============

.. image:: _static/structure/settings.png


Gordon ``settings.yml`` files are simple `yaml <http://yaml.org/>`_ files which define how Gordon
should behave.

Settings can be defined at two different levels, project and application level.

Resources such as lambdas or event sources can be defined in both levels, but there are
some other settings which are only expected at project level.

General
--------

These settings can be defined either at project or app level.

=====================  =================================================================================================================================================
Settings               Description
=====================  =================================================================================================================================================
``lambdas``            Lambda definitions. :ref:`Anatomy of Lambdas <lambdas-anatomy>`
``cron``               CloudWatch Events definitions. :ref:`Anatomy of Cron integration <events-anatomy>`
``dynamodb``           Dynamodb Event Source definitions. :ref:`Anatomy of Dynamodb integration <dynamodb-anatomy>`
``kinesis``            Kinesis Event Source definitions. :ref:`Anatomy of Kinesis integration <kinesis-anatomy>`
``s3``                 S3 notfication definitions. :ref:`Anatomy of S3 integration <s3-anatomy>`
``apigateway``         API Gateway definitions. :ref:`Anatomy of Api Gateway integration <apigateway-anatomy>`
``aws-account-id``     AWS account id where you are deploying your lambdas. If not present, gordon will try to retrieve it using IAM api.
=====================  =================================================================================================================================================


Project settings
--------------------

Project settings are defined in the root level of your project  (``project/settings.yml``). The section :ref:`Project Anatomy <project-anatomy>` will give you more information about how
you can customize your project.


Application settings
----------------------

Application settings are defined within your applications (``application/settings.yml``).

One particularity about application settings, is that those can be redefined as part of it's initialization. If for example you want to reuse one application and
redefining some settings, you can do so:

.. code-block:: yaml

  ---
  project: my-project
  default-region: eu-west-1
  code-bucket: my-bucket
  apps:
    - exampleapp
    - exampleapp:
        a: b
        c: d
  ...
