Settings
============

.. image:: _static/structure/settings.png


Gordon ``settings.yml`` files are simple `yaml <http://yaml.org/>`_ files which define how Gordon
should behave.

Settings can be defined at two different levels, project and application level.

Resources such as lambdas or event sources can be defined in both levels, but there are
some other settings which are only expected at project level.

Project settings
--------------------

Project settings are defined in the root level of your project.

=====================  ==========================================================================================================================================
Settings               Description
=====================  ==========================================================================================================================================
``project``            Name of the project
``default-region``     Default region where the project will be deployed
``code-bucket``        Name of the bucket gordon will use to store the source code of your lambdas and cloudformation templates.
                       Because the source code and the lambdas needs to be in the same region, gordon will create on bucket per region and stage.
``apps``               List of installed apps
=====================  ==========================================================================================================================================


Application settings
----------------------

Application settings are defined within your applications.

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
