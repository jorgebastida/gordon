Apigateway
========================

Amazon API Gateway is a fully managed service that makes it easy for developers to create APIs at any scale.

Gordon allow you to create and integrate your Lambdas with apigateway resources in order to easily create HTTP APIs.

It might be interesting for you to give it a look to `AWS: Amazon API Gateway Concepts <http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-basic-concept.html>`_
before continuing.

.. _apigateway-anatomy:

Anatomy of the integration
----------------------------------

 .. code-block:: yaml

  apigateway:

    { API_NAME }:
      description: { STRING }
      cli-output: { BOOLEAN }
      resources:
        { URL }:
            methods: { LIST }
            api_key_required: { BOOL }
            authorization_type: { STRING }
            responses: { LIST }
            parameters: { MAP }
            request_templates: { MAP }
            integration:
                type: { STRING }
                lambda: { LAMBDA_NAME }
                http_method: { STRING }
                responses: { LIST }
                parameters: { MAP }



Properties
-------------------


Api Name
^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         Key of the ``apigateway`` map.
Required                     Yes
Valid types                  ``string``
Max length                   30
Description                  Name for your apigateway.
===========================  ============================================================================================================


Description
^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         ``description``
Required                     No
Default                      *Empty*
Valid types                  ``string``, ``reference``
Max length                   30
Description                  Description of your api
===========================  ============================================================================================================

cli-output
^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         ``cli-output``
Required                     No
Default                      True
Valid types                  ``boolean``
Description                  Output the deployment base URL as part of the ``apply`` output
===========================  ============================================================================================================


Resources
^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         ``resources``
Required                     Yes
Valid types                  ``map``
Description                  Resources of your API Gateway
===========================  ============================================================================================================

Example:

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


Resource URL
^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         Key of the ``resources`` map.
Required                     Yes
Valid types                  ``string``
Description                  Full path (url) of your resource
===========================  ============================================================================================================

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

Resource Methods
^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         ``methods``
Required                     Yes
Valid types                  ``list``, ``string``, ``map``
Description                  List of valid methods for your resource
===========================  ============================================================================================================

Example:

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

Resource Methods (advanced)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The simplified version of ``methods`` is only a shortcut in order to make gordon's API nicer 95% of the time.

That version (the simplified one) should be more than enough for most of the cases, but if for some reason you want to
be able to configure different integrations for each of the methods of an url, you'll need to make ``methods`` a map of
http methods to integrations.

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


Resource authorization type
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


===========================  ============================================================================================================
Name                         ``api_key_required``
Required                     No
Default                      ``False``
Valid Types                  ``Boolean``
Description                  Indicates whether the method requires clients to submit a valid API key.
===========================  ============================================================================================================


===========================  ============================================================================================================
Name                         ``authorization_type``
Required                     No
Default                      ``NONE``
Valid Values                 ``NONE``
Description                  Authorization type (if any) for your resource.
===========================  ============================================================================================================


Resource Responses
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         ``responses``
Required                     No
Valid Types                   ``Response``
Description                  Responses that can be sent to the client who calls this resource.
===========================  ============================================================================================================

Example:

.. code-block:: yaml

    apigateway:
        helloapi:
            resources:
                /hello:
                    method: GET
                    integration:
                        lambda: helloworld.sayhi
                        responses:
                            - code: "404"
                    responses:
                        - pattern: ""
                          code: "404"


Resource Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

===========================  ===========================================================================================================================
Name                         ``parameters``
Required                     No
Default                      *Empty*
Valid Values                 ``MAP``
Description                  Request parameters that API Gateway accepts. Specify request parameters as key-value pairs (string-to-Boolean maps),
                             with a source as the key and a Boolean as the value. The Boolean specifies whether a parameter is required.
                             A source must match the following format ``method.request.$location.$name``, where the ``$location`` is ``querystring``,
                             ``path``, or ``header``, and ``$name`` is a valid, unique parameter name.
===========================  ===========================================================================================================================


Resource Request Templates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

===========================  ==================================================================================================================================
Name                         ``request_templates``
Required                     No
Valid Values                 ``map``
Description                  A map of Apache Velocity templates that are applied on the request payload. The template that API Gateway
                             uses is based on the value of the Content-Type header sent by the client. The content type value is the
                             key, and the template is the value (specified as a string).
                             For more information: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-mapping-template-reference.html
===========================  ==================================================================================================================================



Resource Integration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         ``integration``
Required                     No
Valid Values                 ``map``
Description                  Integration for the current Resource
===========================  ============================================================================================================


Integration Type
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         ``type``
Required                     No
Default                      AWS
Valid Values                 ``AWS``, ``MOCK``, ``HTTP``
Description                  Type of the integration
===========================  ============================================================================================================


Integration Lambda
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         ``lambda``
Required                     Depends
Valid Values                 ``app.lambda-name``
Description                  Name of the lambda you want to configure for this resource.
===========================  ============================================================================================================

Integration Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

===========================  ==============================================================================================================================
Name                         ``parameters``
Required                     No
Default                      *Empty*
Valid Values                 ``MAP``
Description                  The request parameters that API Gateway sends with the back-end request. Specify request parameters as key-value pairs
                             (string-to-string maps), with a destination as the key and a source as the value. Specify the destination using the
                             following pattern ``integration.request.$location.$name``, where ``$location`` is ``querystring``, ``path``, or ``header``,
                             and ``name`` is a valid, unique parameter name. The source must be an existing method request parameter or a static value.
                             Static values must be enclosed in single quotation marks and pre-encoded based on their destination in the request.
===========================  ==============================================================================================================================

Integration HTTP Method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         ``http_method``
Required                     Depends
Valid Values                 ``string``
Description                  Http method the ApiGateway will use to contact the integration
===========================  ============================================================================================================

Integration Responses
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

===========================  ============================================================================================================
Name                         ``responses``
Required                     No
Valid Values                 ``list``
Description                  The response that API Gateway provides after a method's back end completes processing a request.
                             API Gateway intercepts the integration's response so that you can control how API Gateway surfaces back-end
                             responses. Each response item can conatain the following keys: ``pattern``: a regular expression that
                             specifies which error strings or status codes from the back end map to the integration response; ``code``:
                             the status code that API Gateway uses to map the integration response to a MethodResponse status code;
                             ``template``: the templates used to transform the integration response body; ``parameters``: the response
                             parameters from the back-end response that API Gateway sends to the method response. Parameters can be used
                             to set outbound CORS headers: ``method.response.header.Access-Control-Allow-Origin: "'*'"`` or to map custom
                             dynamic headers: ``method.response.header.Custom: "integration.response.body.customValue"``


===========================  ============================================================================================================

Example:

.. code-block:: yaml

    apigateway:
      helloapi:
        resources:
          /hello:
            method: GET
            integration:
              lambda: helloworld.sayhi
              responses:
                - pattern: ""
                  code: "404"
                  models:
                    application/xml: Empty
                  template:
                    application/json: |
                      #set($inputRoot = $input.path('$'))
                      $inputRoot



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

                /parameters:
                    methods: GET
                    parameters:
                        method.request.header.color: True
                    integration:
                        lambda: helloworld.hellopy
                        responses:
                            - pattern: ""
                              code: "200"
                        parameters:
                            integration.request.querystring.color: method.request.header.color
                    responses:
                        - code: "200"
                          parameters:
                              method.response.header.color: color

                /cors:
                    methods: GET
                    integration:
                        lambda: helloworld.hellopy
                        responses:
                            - pattern: ""
                              code: "200"
                              parameters:
                                  method.response.header.Access-Control-Allow-Origin: "'*'"
                                  method.response.header.Access-Control-Allow-Methods: "'*'"
                                  method.response.header.Access-Control-Request-Method: "'GET'"
                    responses:
                        - code: "200"
                          parameters:
                              method.response.header.Access-Control-Allow-Origin: true
                              method.response.header.Access-Control-Allow-Methods: true
                              method.response.header.Access-Control-Request-Method: true

                /hi/complex/:
                    methods:
                        GET:
                            integration:
                                lambda: helloworld.sayhi
                        POST:
                            integration:
                                lambda: helloworld.sayhi

                /content-types:
                    methods: POST
                    integration:
                        lambda: helloworld.sayhi
                        responses:
                            - pattern: ""
                              code: "200"
                              template:
                                  application/json: |
                                    #set($inputRoot = $input.path('$'))
                                    $inputRoot

                    request_templates:
                        application/x-www-form-urlencoded: |
                            #set($inputRoot = $input.path('$'))
                            {}
                    responses:
                        - code: "200"
                          models:
                              application/xml: Empty
