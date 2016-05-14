Gordon tests are split between three types:

1. Core Tests: Test that gordon internals behave as expected
2. Build tests: Based on gordon projects, test that the output of the build command is the expected one.
3. Integration tests: Based on gordon projects, test that running build and apply generates the expected resources on AWS.


|                   | Internet Access | AWS Credentials |    Speed    |
|:-----------------:|:---------------:|:---------------:|:-----------:|
|     Core Tests    |        No       |        No       |     Fast    |
|    Build Tests    |       Yes       |        No       |     Fast    |
| Integration Tests |       Yes       |       Yes       | Really Slow |


How to run all ``core`` and ``build`` tests?
---------------------------------------------

```shell
python setup.py nosetests -a '!integration'
```


How to run all ``integration`` tests?
---------------------------------------

```shell
python setup.py nosetests -a 'integration' --stop --nologcapture
```

How to run one ``integration`` test?
-------------------------------------

```shell
python setup.py nosetests -a 'integration' --stop --nologcapture --where=tests/lambdapython/
```


How to run coverage
--------------------------------

```shell
coverage run --source=gordon setup.py nosetests -a 'integration' --stop --nologcapture
```
