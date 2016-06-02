Simple ES6 Javascript Example
================================

This project defines one lambda called ``hellojs`` implemented using [ES6](https://github.com/lukehoban/es6features)

The lambda itself is quite dumb, and only prints ``Hello from ES6!``, but the important bit is
that we have replaced the default ``build`` process for that lambda with a custom one which which will
transpile the code using babel.

In order to do so, we have create a script called ``build`` in our ``package.json`` which calls babel:

```json
{
  ...
  "scripts": {
      "build": "babel *.js --out-dir $TARGET"
  }
}
```

And then make the build process our lambda call it.

```yaml
lambdas:
  hellojs:
    code: hellojs
    runtime: nodejs4.3
    handler: code.handler
    build: TARGET={target} npm run build
```

As result, your transpiled ``code.js`` will end up in the ``TARGET`` directory, and gordon will
package it inside the ``.zip`` file of your lambda.


Documentation relevant to this example:
 * [Lambdas](http://gordon.readthedocs.io/en/latest/lambdas.html)
 * [Lambdas Build](http://gordon.readthedocs.io/en/latest/lambdas.html#build)

How to deploy it?
------------------

* ``$ gordon build``
* ``$ gordon apply``
