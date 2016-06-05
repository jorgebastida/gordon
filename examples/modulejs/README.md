Module Javascript Example
===========================

This simple project defines one lambda called ``byejs``. This lambda is what is called a "module" lambda
because the code of it is in a directory instead of a single file.

Inside the directory ``bye`` we have defined two files:

```shell
bye
├── code.js
└── package.json
```

* ``code.js`` contains the code of our lambda.
* ``package.json`` defines some dependencies needed.

When your project is build, gordon will install all the dependencies you have defined in your ``package.json``
file and will bundle them together before uploading your lambda to AWS.

The lambda is quite dumb, and only and example.

Documentation relevant to this example:
 * [Lambdas](https://gordon.readthedocs.io/en/latest/lambdas.html)
 * [Javascript Requirements](https://gordon.readthedocs.io/en/latest/requirements.html#javascript-requirements)

How to deploy it?
------------------

* ``$ gordon build``
* ``$ gordon apply``
