Docker Example
===========================

Example project, which builds lambdas within a Docker container instead of in your host.

In this example, we use [lambci/docker-lambda](https://github.com/lambci/docker-lambda) as base images, as
they are almost identical to the environment where the lambdas are going to run.

Documentation relevant to this example:
 * [Lambdas](https://gordon.readthedocs.io/en/latest/lambdas.html)

How to deploy it?
------------------

* Install [Docker](https://docs.docker.com/engine/installation/)
* ``eval $(docker-machine env default)`` Replace ``default`` with your appropriate value.
* ``$ gordon build``
* ``$ gordon apply``
