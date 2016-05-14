Apigateway
========================

Amazon API Gateway is a fully managed service that makes it easy for developers to create APIs at any scale.

Gordon allow you to create and integrate your Lambdas with apigateway resources in order to easily create HTTP APIs.


.. _apigateway-anatomy:

Anatomy of the integration
----------------------------------

 .. code-block:: yaml

  apigateway:

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

Map of apigateway resources with their implementations. The key name of the resources will be
the full path (url) they will have within your apigateway.

.. code-block:: yaml

    apigateway:
        firstapi:
            description: My Inventory
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
            description: My Inventory API
            resources:
                /:
                    methods: GET
                    lambda: inventory.index
                /article/{article_id}:
                    methods: POST
                    lambda: inventory.article

Your lambda called ``shop.article`` will receive one parameter called ``article_id``.

Resources: Methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

List of HTTP methods you lambda will support.

.. code-block:: yaml

    apigateway:
        example:
            description: My Api example
            resources:
                /:
                    methods: GET
                    lambda: inventory.index
                /get_and_post:
                    methods: [GET, POST]
                    lambda: inventory.article
                /get_post_and_delete:
                    methods:
                        - GET
                        - POST
                        - DELETE
                    lambda: inventory.article


.. note::

  As shortcut, if ``methods`` value is a string instead of a list gordon will assume you only want one method.


Resources: Methods (advanced)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Methods is more than only a list of strings. The simplified version is only a shortcut in order to make gordon's API nicer 95% of the time.

That version (the simplified one) should be more than enough for most of the cases, but if for some reason you want to
be able to configure different integrations for each of the methods of an url, you'll need to do this.

.. code-block:: yaml

  apigateway:
    exampleapi:
      description: My not-that-simple example
      resources:
        /:
          methods:
            GET:
              integration:
                lambda: app.index_on_get
            POST:
              integration:
                lambda: app.index_on_post

.. note::

    If you use this approach, you would need to define **ALL** resource settings at the level of each method in your resource.


Authorization type
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

apigateway authorization type for this resouce. The only (and default) authorization type is ``NONE``.


Full Example
----------------------------------

.. code-block:: yaml

    apigateway:

        helloapi:

            description: My complex hello API
            resources:
                /:
                    methods: GET
                    integration:
                        lambda: helloworld.sayhi
                /hi:
                    methods: [GET, POST]
                    integration:
                        lambda: helloworld.sayhi

                /hi/with-errors:
                    method: GET
                    integration:
                        lambda: helloworld.sayhi
                        responses:
                            - code: "404"
                    responses:
                        - pattern: ""
                          code: "404"

                /hi/none:
                    method: GET

                /hi/http:
                    methods: GET
                    integration:
                        type: HTTP
                        uri: https://www.google.com

                /hi/mock:
                    methods: GET
                    integration:
                        type: MOCK

                /hi/complex/:
                    methods:
                        GET:
                            integration:
                                lambda: helloworld.sayhi
                        POST:
                            integration:
                                lambda: helloworld.sayhi
