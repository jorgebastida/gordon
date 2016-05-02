Apigateway
========================

Amazon API Gateway is a fully managed service that makes it easy for developers to create APIs at any scale.

Gordon allow you to create and integrate your Lambdas with Apigateway resources in order to easily create HTTP APIs.


.. _apigateway-anatomy:

Anatomy of the integration
----------------------------------

 .. code-block:: yaml

  apigateeway:

    { API_NAME }:
      description: { API_DESCRIPTION }
      resources:
        { URL }:
            method: { HTTP_METHOD }
            methods: { LIST_OF_HTTP_METHODS }
            lambda: { LAMBDA_NAME }
            authorization_type: { AUTHORIZATION_TYPE }
            type: { INTEGRATION_TYPE }
            integration_http_method: { INTEGRATION_HTTP_METHOD }
            integration_responses: { INTEGRATION_RESPONSES }
            method_responses: { METHOD_RESPONSES }


Api Description
---------------------

Description for your API.


Resources
^^^^^^^^^

Resources is a map that contains all the urls of your api. The value of each key is the related configuration for that url.



Full Example
----------------------------------

.. code-block:: yaml

    apigateway:

        helloapi:
            description: My first API
            resources:
                /:
                    methods: [GET, POST]
                    lambda: helloworld.hellopy
                /hi:
                    method: GET
                    lambda: helloworld.hellopy

                /hi/poo:
                    method: GET
                    lambda: helloworld.hellopy
                    responses:
                        - code: "404"
                    responses:
                        - pattern: ""
                          code: "404"

                /hi/none:
                    method: GET

                /extra/super/lol/:
                    methods:
                        GET:
                            lambda: helloworld.hellopy
                        POST:
                            lambda: helloworld.hellopy
