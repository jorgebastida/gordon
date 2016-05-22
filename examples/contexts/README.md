Gordon Contexts Example
===========================

![gordon](http://gordondoc.s3-website-eu-west-1.amazonaws.com/_static/examples/contexts.svg)

This simple project defines three Lambdas called ``hellopy``, ``hellojs`` and ``hellojava``.
Each of these lambdas are written in one different language, but they do pretty much the same.

As well as the lambdas, this project defines that the context called ``default`` has three
variables: ``username``, ``password`` and ``bucket``. All three will have a dynamic value
based on the stage we deploy them, hence that the value starts with ``ref://``.

This project has a directory called ``parameters`` with three files in it: ``common.yml``,
``dev.yml`` and ``prod.yml``. When you apply your project in the stage ``dev`` gordon
will gather and merge settings from ``common.yml`` and ``dev.yml``, and resolve the references
in your ``default`` context, giving it the value of:

```json
{"username": "my_username", "password": 123456, "bucket": "images-bucket-dev"}
```

Then, on apply time, gordon will inject a file called ``.context`` to your lambda ``.zip``
before uploading it to AWS.

These three lambdas will hey read a file called ``.context`` that gordon

These three lambdas defined within the application ``helloworld`` read the ``.contex`` file
and return the value of the key ``bucket``.

Documentation relevant to this example:
 * [Lambdas](http://gordondoc.s3-website-eu-west-1.amazonaws.com/lambdas.html)
 * [Contexts](http://gordondoc.s3-website-eu-west-1.amazonaws.com/contexts.html)
 * [Parameters](http://gordondoc.s3-website-eu-west-1.amazonaws.com/parameters.html)
 * [Advanced Parameters](http://gordondoc.s3-website-eu-west-1.amazonaws.com/parameters_advanced.html)

How to deploy it?
------------------

* ``$ gordon build``
* ``$ gordon apply``
