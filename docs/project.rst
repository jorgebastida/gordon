Project
===========

.. image:: _static/structure/project.png

Projects are root concept which contain all other resources. Projects are composed of:

  * :doc:`apps`
  * :doc:`settings`

Once you start using gordon, you'll realize it makes sense to have several projects, and not only one monolitic one with dozens of applications.

This is not news to you if you have heard about microservices, but it is good to emphasize that massive projects might not a good idea (generally speaking).

As always, give it a shoot and decide what is better for you.

How can I create a new project?
--------------------------------

Creating a new project is easy, you only need to run the following command:

.. code-block:: bash

    $ gordon startproject demo

This will create a new directory called ``demo`` which will contain the most basic project. That's a single ``settings.yml`` file:

.. code-block:: bash

    demo
    └── settings.yml


Project Settings
--------------------

You can read a full in-depth explanation of how settings works in the :doc:`settings` page, but these are the most common project settings you'll probably use:

.. code-block:: yaml

  ---
  project: { PROJECT_NAME }
  default-region: { PROJECT_DEFAULT_REGION }
  code-bucket: { S3_BUCKET }
  apps:
    - { APPLICATION }

  dynamodb:
    ...

  kinesis:
    ...

  s3:
    ...

By default when you create a project, gordon will include some applications which you'll probably need. Those applications are called :doc:`contrib`
applications and provide you (and your gordon project) with some basic functionalities that you (or gordon) might need.


Project Actions
-----------------

Once you have created your project, there are two main actions that you'll run from the command line; ``build`` and ``apply``.

build
^^^^^^

Build is the action that will collect all registered resources in your project, and create several
templates in the ``_build`` directory which will represent everything you have defined.
As well as creating these templates, gordon will create all necessary artifacts that it'll later upload to s3.

At this point, gordon will not use any AWS credentials. This is important.

What gordon generates in the build directory is merely declarative and completely agnostic of in which region or stage you'll (later)
deploy it, as well as doesn't know/care what is the current status (if any) of all those resources.

This is one of the greatness (and technical challenges) of gordon.

The number of required templates depend on you project, but these are all possible templates gordon will create:

=====================  ==================  ==============================================================================
Acronym                Name                Description
=====================  ==================  ==============================================================================
``pr_p.json``          Pre Project         Custom template - This is not generally used
``p.json``             Project             CloudFormation template - Gordon will create a S3 bucket where it'll upload your lambdas
``pr_r.json``          Pre Resources       Custom template - Gordon will generally upload your lambdas to S3.
``r.json``             Resources           CloudFormation template - Gordon will create your lambdas and event sources
``ps_r.json``          Post Resources      Custom template - This is not generally used
=====================  ==================  ==============================================================================


apply
^^^^^^^

Apply is the action that will deploy your project to one specific region and stage.

=====================  ================================================================================================
Term                   Description
=====================  ================================================================================================
``region``             AWS cloud is divided in several regions. Each Region is a separate geographic area. `AWS Regions and Availability Zones <http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html>`_
``stage``              Stages are 100% isolated deployments of the same project. The idea is that the same project can be deployed in the same AWS account in different stages (``dev``, ``staging``, ``prod``...) in order to SAFELY test it's behaviour.
=====================  ================================================================================================

This command will:

  * Collect all required parameters for this stage.
  * Sequentially apply all gordon templates.

This command (for obvious reasons), will use your AWS credentials to apply your project templates.
