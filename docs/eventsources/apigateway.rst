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
            methods: { LIST_OF_HTTP_METHODS }
            authorization_type: { AUTHORIZATION_TYPE }
            responses: { METHOD_RESPONSES }
            integration:
                type: { INTEGRATION_TYPE }
                lambda: { LAMBDA_NAME }
                http_method: { INTEGRATION_HTTP_METHOD }
                responses: { INTEGRATION_RESPONSES }



Api Description
---------------------

Description for your API.


Resources
-------------------

Map of apigateway resources with their implementations. The key name of the resources would be
the full path (url) they will have within your apigateway.

.. code-block:: yaml

    apigateway:
        firstapi:
            description: My first API
            resources:
                /:
                    methods: GET
                    lambda: helloworld.index
                /contact/email:
                    methods: POST
                    lambda: helloworld.contact


In this example, we have defined one API called ``firstapi`` with two resources: ``/`` and ``/contact/email``:

 * Each of these urls will call two different lambdas ``helloworld.index`` and ``helloworld.contact`` respectively.
 * The first url ``/`` will only allow ``GET`` requests, and the second one ``/contact/email`` will only allow ``POST`` requests.

Each of the resources can be further configured using any of the following properties.


Resources: URL
^^^^^^^^^^^^^^^^

``URLs`` are the key of the resources map. For each resource. You need to define the full path including the leading ``/``.

If you want to make certain urls have parameters, you can do so using apigatweway syntax.

.. code-block:: yaml

    apigateway:
        myshop:
            description: My first API
            resources:
                /:
                    methods: GET
                    lambda: shop.index
                /article/{article_id}:
                    methods: POST
                    lambda: shop.article

Your lambda called ``shop.article`` will receive one parameter called ``article_id``.


Full Example
----------------------------------

.. code-block:: yaml

    apigateway:

        helloapi:

            description: My complex hello API
            resources:
                /:
                    methods: GET
                    lambda: helloworld.hellopy
                /hi:
                    methods: GET
                    lambda: helloworld.hellopy

                /hi/with-errors:
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
