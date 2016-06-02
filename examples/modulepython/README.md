Module Python Example
===========================

This simple project defines one lambda called ``hellopython``. This lambda is what is called a "module" lambda
because the code of it is in a directory instead of a single file.

Inside the directory ``hello`` we have defined two files:

```shell
hello
├── code.py
└── requirements.txt
```

* ``code.py`` contains the code of our lambda.
* ``requirements.txt`` defines some requirements needed.

When your project is build, gordon will install all the requirements you have defined in your ``requirements.txt``
file and will bundle them together before uploading your lambda to AWS.

The lambda is quite dumb, and only an example.

Documentation relevant to this example:
 * [Lambdas](http://gordon.readthedocs.io/en/latest/lambdas.html)
 * [Python Requirements](http://gordon.readthedocs.io/en/latest/requirements.html#python-requirements)

How to deploy it?
------------------

* ``$ gordon build``
* ``$ gordon apply``
