import copy
import uuid
import hashlib

import six
import troposphere
from troposphere.apigateway import (
    RestApi, Resource, Method, Integration, Deployment, MethodResponse,
    IntegrationResponse
)

from gordon import utils, exceptions
from .base import BaseResource


LAMBDA_INTEGRATION = 20
HTTP_INTEGRATION = 30
MOCK_INTEGRATION = 40


class ApiGateway(BaseResource):

    grn_type = 'apigateway'

    def __init__(self, *args, **kwargs):
        super(ApiGateway, self).__init__(*args, **kwargs)
        self._resources = {}

    def get_or_create_resource(self, path, api, template):
        """Returns the ID of the Resource ``path`` in ``api``.
        If the resorce doesn't exits, create a new one and add it to
        ``template``."""

        # Add leading slash
        if path and path[0] != '/':
            path = '/{}'.format(path)

        # Remove trailing slash
        if path and path[-1] == '/':
            path = path[:-1]

        # Make / the root path
        if not path:
            path = '/'

        # Return API root resource if
        if path == '/':
            return troposphere.GetAtt(api, 'RootResourceId')

        if path in self._resources:
            return self._resources[path]

        parent_path, path_part = path.rsplit('/', 1)
        parent_id = self.get_or_create_resource(parent_path, api, template)
        resource = Resource(
            utils.valid_cloudformation_name(self.name, 'Resource', *path.split('/')),
            ParentId=parent_id,
            PathPart=path_part,
            RestApiId=troposphere.Ref(api)
        )

        template.add_resource(resource)
        self._resources[path] = troposphere.Ref(resource)
        return self._resources[path]

    def get_function_name(self, resource):
        """Returns a reference to the current alias of the lambda which will
        process this stream."""
        return self.project.reference(
            utils.lambda_friendly_name_to_grn(resource['integration']['lambda'])
        )

    def get_authorization_type(self, resource):
        return resource.get('authorization_type', 'NONE')

    def get_api_key_required(self, resource):
        return self._get_true_false('api_key_required', 'f', settings=resource)

    def get_integration_http_method(self, resource):
        http_method = resource['integration'].get('http_method')
        if http_method:
            return http_method

        integration_type = self._get_integration_type(resource)
        if integration_type == LAMBDA_INTEGRATION:
            return 'POST'
        else:
            return 'GET'

    def _get_integration_type(self, resource):
        if 'integration' not in resource:
            raise exceptions.InvalidApigatewayIntegrationTypeError("Resource has no integration".format(resource))
        if 'lambda' in resource['integration']:
            return LAMBDA_INTEGRATION
        elif resource['integration']['type'] == 'HTTP':
            return HTTP_INTEGRATION
        elif resource['integration']['type'] == 'MOCK':
            return MOCK_INTEGRATION
        raise exceptions.InvalidApigatewayIntegrationTypeError(resource['integration'])

    def get_integration_type(self, resource):
        integration = self._get_integration_type(resource)
        if integration == HTTP_INTEGRATION:
            return 'HTTP'
        elif integration == MOCK_INTEGRATION:
            return 'MOCK'
        elif integration == LAMBDA_INTEGRATION:
            return 'AWS'
        return None

    def get_integration_credentials(self, resource, invoke_lambda_role):
        if self._get_integration_type(resource) == LAMBDA_INTEGRATION:
            return troposphere.GetAtt(invoke_lambda_role, 'Arn')
        return troposphere.Ref(troposphere.AWS_NO_VALUE)

    def get_integration_uri(self, resource):
        integration_type = self._get_integration_type(resource)
        if integration_type == LAMBDA_INTEGRATION:
            return troposphere.Join(
                '',
                [
                    'arn:aws:apigateway:',
                    troposphere.Ref(troposphere.AWS_REGION),
                    ':lambda:path/2015-03-31/functions/',
                    troposphere.Ref(self.get_function_name(resource)),
                    '/invocations'
                ]
            )
        elif integration_type == HTTP_INTEGRATION:
            return resource['integration']['uri']
        elif integration_type == MOCK_INTEGRATION:
            return troposphere.Ref(troposphere.AWS_NO_VALUE)

    def get_method_responses(self, resource):
        default_method_responses = [
            {'code': '200'}
        ]
        responses = []
        for response in resource.get('responses', default_method_responses):
            extra = {}
            if 'models' in response:
                extra['ResponseModels'] = response['models']
            if 'parameters' in response:
                extra['ResponseParameters'] = response['parameters']
            responses.append(
                MethodResponse(
                    StatusCode=six.text_type(response['code']),
                    **extra
                )
            )
        return responses

    def get_integration_responses(self, resource):
        default_integration_responses = [
            {'pattern': '', 'code': '200'}
        ]
        responses = []
        for response in resource['integration'].get('responses', default_integration_responses):
            extra = {}
            if 'template' in response:
                extra['ResponseTemplates'] = response['template']
            responses.append(
                IntegrationResponse(
                    SelectionPattern=six.text_type(response['pattern']),
                    StatusCode=six.text_type(response['code']),
                    **extra
                )
            )
        return responses

    def get_request_templates(self, resource):
        return resource.get('request_templates', {})

    def get_integration(self, resource, invoke_lambda_role):
        integration_type = self.get_integration_type(resource)
        if integration_type:
            extra = {}
            if 'parameters' in resource['integration']:
                extra['RequestParameters'] = resource['integration']['parameters']
            return Integration(
                IntegrationResponses=self.get_integration_responses(resource),
                IntegrationHttpMethod=self.get_integration_http_method(resource),
                Type=integration_type,
                Credentials=self.get_integration_credentials(resource, invoke_lambda_role),
                RequestTemplates=self.get_request_templates(resource),
                Uri=self.get_integration_uri(resource),
                **extra
            )
        return troposphere.Ref(troposphere.AWS_NO_VALUE)

    def register_resources_template(self, template):

        deployment_resources = []
        api = RestApi(
            self.in_project_cf_name,
            Name=troposphere.Join("-", [self.name, troposphere.Ref('Stage')]),
            Description=self.settings.get('description', '')
        )
        template.add_resource(api)
        deployment_resources.append(api)

        invoke_lambda_role = troposphere.iam.Role(
            utils.valid_cloudformation_name(self.name, 'Role'),
            AssumeRolePolicyDocument={
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {
                        "Service": ["apigateway.amazonaws.com"]
                    },
                    "Action": ["sts:AssumeRole"]
                }]
            },
            Policies=[
                troposphere.iam.Policy(
                    PolicyName=utils.valid_cloudformation_name(self.name, 'Role', 'Policy'),
                    PolicyDocument={
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "lambda:InvokeFunction"
                                ],
                                "Resource": [
                                    "*"
                                ]
                            }
                        ]
                    }
                )
            ]
        )

        template.add_resource(invoke_lambda_role)
        deployment_resources.append(invoke_lambda_role)

        deployment_dependencies = []
        for path, resource in six.iteritems(self.settings.get('resources', {})):
            resource_reference = self.get_or_create_resource(path, api, template)
            methods = resource['methods']

            if isinstance(methods, six.string_types):
                methods = [methods]

            if not isinstance(methods, dict):
                method_properties = copy.deepcopy(resource)
                method_properties.pop('methods', None)
                methods = dict([[method, method_properties] for method in methods])

            for method, configuration in six.iteritems(methods):
                method_name = [self.name]
                method_name.extend(path.split('/'))
                method_name.append(method)

                extra = {}
                if 'parameters' in configuration:
                    extra['RequestParameters'] = configuration['parameters']
                m = Method(
                    utils.valid_cloudformation_name(*method_name),
                    HttpMethod=method,
                    AuthorizationType=self.get_authorization_type(configuration),
                    ApiKeyRequired=self.get_api_key_required(configuration),
                    Integration=self.get_integration(configuration, invoke_lambda_role),
                    MethodResponses=self.get_method_responses(configuration),
                    ResourceId=resource_reference,
                    RestApiId=troposphere.Ref(api),
                    **extra
                )
                template.add_resource(m)
                deployment_dependencies.append(m.name)
                deployment_resources.append(m)

        deploy_hash = hashlib.sha1(six.text_type(uuid.uuid4()).encode('utf-8')).hexdigest()
        deploy = Deployment(
            utils.valid_cloudformation_name(self.name, "Deployment", deploy_hash[:8]),
            DependsOn=sorted(deployment_dependencies),
            StageName=troposphere.Ref('Stage'),
            RestApiId=troposphere.Ref(api)
        )

        template.add_resource(deploy)

        if self._get_true_false('cli-output', 't'):
            template.add_output([
                troposphere.Output(
                    utils.valid_cloudformation_name("Clioutput", self.in_project_name),
                    Value=troposphere.Join(
                        "",
                        [
                            "https://",
                            troposphere.Ref(api),
                            ".execute-api.",
                            troposphere.Ref(troposphere.AWS_REGION),
                            ".amazonaws.com/",
                            troposphere.Ref('Stage')
                        ]
                    ),
                )
            ])
