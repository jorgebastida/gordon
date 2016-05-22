Lambda Requirements
=====================

``When in Rome do as the Romans``

We believe developers of lambdas should feel like in home while writing them
in their languages. We are not going to come up with a package manager for
javascript or a build tool for java better than the existing ones.

For that reason we try to respect as much as possible each runtime *de facto*
package managers / build tools.

That is the reason why the default ``build`` implementation for each kind
of runtime uses ``pip``, ``npm`` and ``graddle``. If you want to know more
about the ``build`` property of lambdas you can read :ref:`Lambda: build <lambda-build>`.

.. note::

  For using this functionality, you'll need to make the ``code`` path for you lambda be a directory. For more information you can read the ``code`` section in :doc:`lambdas`.


Python requirements
---------------------

If your python lambda requires some python packages, you can create a ``requirements.txt``
file in the root of your lambda folder, and gordon will install all those using ``pip``.

For more information about the format of this file:

    * https://pip.readthedocs.org/en/1.1/requirements.html

Additionally you can customize how gordon invoques ``pip`` using the following settings:

=========================  ====================================================================
Setting                    Description
=========================  ====================================================================
``pip-path``               Path to you pip binary Default: ``pip``
``pip-install-extra``      Extra arguments you want gordon to use while invoking pip install.
=========================  ====================================================================

Example ``requirements.txt``:

.. code-block:: bash

    requests>=2.0
    cfn-response


Javascript requirements
------------------------

If your javascript lambda requires some extra modules, you can create a ``package.json``
file in the root of your lambda folder, and gordon will invoke ``npm install`` for you.

For more information:

    * https://docs.npmjs.com/files/package.json
    * https://docs.npmjs.com/cli/install

Additionally you can customize how gordon invoques ``npm`` using the following settings:

========================  ==================================================================
Setting                   Description
========================  ==================================================================
``npm-path``              Path to you npm binary Default: ``npm``
``npm-install-extra``     Extra arguments you want gordon to use while invoking npm install.
========================  ==================================================================

Example ``package.json``:

.. code-block:: json

    {
      "dependencies": {
        "path": "0.11.14"
      }
    }



Java requirements
---------------------

If your Java lambda requires some extra packages, you can customize how your Java
lambda is built editing your ``dependency`` section in your ``build.gradle`` file.

For more information:

    * https://docs.gradle.org/current/userguide/dependency_management.html

The only requirement gordon enforces to this ``build.gradle`` file is that the
``build`` target leaves whatever you want to get bundled into your lambda in the ``dest`` folder.
You can make this build process as complex as you want/need.


Additionally you can customize how gordon invoques ``gradle`` using the following settings:

========================  ======================================================================
Setting                   Description
========================  ======================================================================
``gradle-path``           Path to you gradle binary Default: ``gradle``
``gradle-build-extra``    Extra arguments you want gordon to use while invoking gradle build.
========================  ======================================================================

Example ``build.grandle``:

.. code-block:: json

    apply plugin: 'java'

    repositories {
        mavenCentral()
    }

    dependencies {
        compile (
            'com.amazonaws:aws-lambda-java-core:1.1.0',
            'com.amazonaws:aws-lambda-java-events:1.1.0'
        )
    }

    task buildLambda(type: Copy) {
        from compileJava
        from processResources
        into('lib') {
            from configurations.runtime
        }
        into target
    }

    build.dependsOn buildLambda
