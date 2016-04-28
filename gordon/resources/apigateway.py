import troposphere
from troposphere.apigateway import RestApi, Resource, Method, Integration, Deployment, MethodResponse, IntegrationResponse

from gordon import utils
from .base import BaseResource


class ApiGatewayContexts(BaseResource):

    grn_type = 'apigateway'

    def __init__(self, *args, **kwargs):
        super(ApiGatewayContexts, self).__init__(*args, **kwargs)
        self._resources = {}

    def get_or_create_resource(self, path, api, template):

        if path and path[0] != '/':
            path = '/{}'.format(path)

        if path and path[-1] == '/':
            path = path[:-1]

        if not path:
            path = '/'

        if path == '/':
            return troposphere.GetAtt(api, 'RootResourceId')

        if path in self._resources:
            return self._resources[path]

        parent_id = self.get_or_create_resource(path.rsplit('/', 1)[0], api, template)
        resource = Resource(
            utils.valid_cloudformation_name(self.name, 'Resource', *path.split('/')),
            ParentId=parent_id,
            PathPart=path.rsplit('/', 1)[1],
            RestApiId=troposphere.Ref(api)
        )

        template.add_resource(resource)
        self._resources[path] = troposphere.Ref(resource)
        return self._resources[path]

    def get_function_name(self, resource):
        """Returns a reference to the current alias of the lambda which will
        process this stream."""
        return self.project.reference(
            utils.lambda_friendly_name_to_grn(resource['integration'].get('lambda'))
        )

    def register_resources_template(self, template):

        api = RestApi(
            self.in_project_cf_name,
            Name=self.name,
            Description=self.settings.get('description', '')
        )
        template.add_resource(api)

        role = troposphere.iam.Role(
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

        template.add_resource(role)

        deployment_dependencies = []
        for path, resource in self.settings.get('resources', {}).iteritems():
            resource_reference = self.get_or_create_resource(path, api, template)

            methods = resource.get('methods', [resource.get('method', 'GET')])

            for method in methods:
                method_name = [self.name]
                method_name.extend(path.split('/'))
                method_name.append(method)

                m = Method(
                    utils.valid_cloudformation_name(*method_name),
                    HttpMethod=method,
                    AuthorizationType=resource.get('authorization_type', 'NONE'),
                    Integration=Integration(
                        IntegrationResponses=[
                            IntegrationResponse(
                                SelectionPattern="",
                                StatusCode="200"
                            )
                        ],
                        IntegrationHttpMethod='POST',
                        Type='AWS',
                        Credentials=troposphere.GetAtt(role, 'Arn'),
                        Uri=troposphere.Join(
                            '',
                            [
                                'arn:aws:apigateway:',
                                troposphere.Ref(troposphere.AWS_REGION),
                                ':lambda:path/2015-03-31/functions/{}',
                                troposphere.Ref(self.get_function_name(resource)),
                                '/invocations?Qualifier=current'
                            ]
                        ),
                    ),
                    MethodResponses=[
                        MethodResponse(
                            StatusCode='200'
                        )
                    ],
                    ResourceId=resource_reference,
                    RestApiId=troposphere.Ref(api)
                )
                template.add_resource(m)
                deployment_dependencies.append(m.name)

        deploy = Deployment(
            utils.valid_cloudformation_name(self.name, "Deployment2"),
            DependsOn=deployment_dependencies,
            StageName='dev',
            RestApiId=troposphere.Ref(api)
        )

        template.add_resource(deploy)
