How to run all tests?
---------------------

```shell
python setup.py nosetests'
```

How to run unittests?
---------------------

```shell
python setup.py nosetests -a '!integration'
```


How to run integration tests?
------------------------------

```shell
python setup.py nosetests -a 'integration' --stop --nologcapture
```

How to run one integration test?
--------------------------------

```shell
python setup.py nosetests -a 'integration' --stop --nologcapture --where=integration/lambdapython/
```


How to run coverage
--------------------------------

```shell
coverage run --source=gordon setup.py nosetests -a 'integration' --stop --nologcapture
```
