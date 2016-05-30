Gordon tests are split between three types:

1. Core Tests: Test that gordon internals behave as expected
2. Build tests: Based on gordon projects, test that the output of the build command is the expected one.
3. Integration tests: Based on gordon projects, test that running build and apply generates the expected resources on AWS.


|                   | Internet Access | AWS Credentials |    Speed    |
|:-----------------:|:---------------:|:---------------:|:-----------:|
|     Core Tests    |        No       |        No       |     Fast    |
|    Build Tests    |       Yes       |        No       |     Fine    |
| Integration Tests |       Yes       |       Yes       | Really Slow |


How to run all ``core`` and ``build`` tests?
---------------------------------------------

```shell
tox
```


How to run all ``integration`` tests?
---------------------------------------

```shell
nosetests -a 'integration' --stop --nologcapture
```

How to run one ``integration`` test?
-------------------------------------

```shell
nosetests -a 'integration' --stop --nologcapture tests/projectupdate/
```
