Simple VPC Example
===========================

This simple project defines one lambda called ``hellopy``.

The lambda itself is quite dumb, and only prints information about the ``Hello World`` test event.

This lambda is deployed within an AWS ``VPC``.

```json
{
  "key3": "value3",
  "key2": "value2",
  "key1": "value1"
}
```

Documentation relevant to this example:
 * [Lambdas](https://gordon.readthedocs.io/en/latest/lambdas.html)
 * [Python Requirements](https://gordon.readthedocs.io/en/latest/requirements.html#python-requirements)

How to deploy it?
------------------

* Change the values of ``security-groups`` and ``subnet-ids``.
* ``$ gordon build``
* ``$ gordon apply``
