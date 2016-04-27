import troposphere
from troposphere.apigateway import RestApi, Resource, Method, Integration, Deployment, MethodResponse, IntegrationResponse

from gordon import utils
from .base import BaseResource


class ApiGatewayContexts(BaseResource):

    grn_type = 'apigateway'

    def register_resources_template(self, template):

        api = RestApi(
            self.in_project_cf_name,
            Name=self.name,
            Description=self.settings.get('description', '')
        )
        template.add_resource(api)

        resource = Resource(
            utils.valid_cloudformation_name(self.name, "FirstResource"),
            ParentId=troposphere.GetAtt(api, 'RootResourceId'),
            PathPart='hi',
            RestApiId=troposphere.Ref(api)
        )

        template.add_resource(resource)

        method = Method(
            utils.valid_cloudformation_name(self.name, "FirstResourceGET"),
            HttpMethod='GET',
            AuthorizationType='NONE',
            Integration=Integration(
                IntegrationResponses=[
                    IntegrationResponse(
                        SelectionPattern=".*",
                        StatusCode="200"
                    )
                ],
                IntegrationHttpMethod='GET',
                Type='AWS',
                Uri='arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:936837623851:function:dev-apigateway-r-HelloworldHellopy-1EYA6E6VIU2AW/invocations',   #?Qualifier=current
            ),
            MethodResponses=[
                MethodResponse(
                    StatusCode='200'
                )
            ],
            ResourceId=troposphere.Ref(resource),
            RestApiId=troposphere.Ref(api)
        )

        template.add_resource(method)

        deploy = Deployment(
            utils.valid_cloudformation_name(self.name, "Deployment2"),
            StageName='dev',
            RestApiId=troposphere.Ref(api)
        )

        template.add_resource(deploy)


# class MethodResponse(AWSProperty):
#
#     props = {
#         "ResponseModels": (dict, False),
#         "ResponseParameters": (dict, False),
#         "StatusCode": (basestring, False)
#     }

    #     class Deployment(AWSObject):
    # resource_type = "AWS::ApiGateway::Deployment"
    #
    # props = {
    #     "Description": (basestring, False),
    #     "RestApiId": (basestring, True),
    #     "StageDescription": (StageDescription, False),
    #     "StageName": (basestring, False)
    # }
    #
#
# class Integration(AWSProperty):
#
#     props = {
#         "CacheKeyParameters": ([basestring], False),
#         "CacheNamespace": (basestring, False),
#         "Credentials": (basestring, False),
#         "IntegrationHttpMethod": (basestring, False),
#         "IntegrationResponses": ([IntegrationResponse], False),
#         "RequestParameters": (dict, False),
#         "RequestTemplates": (dict, False),
#         "Type": (basestring, False),
#         "Uri": (basestring, False)
#     }


#
# class Method(AWSObject):
#     resource_type = "AWS::ApiGateway::Method"
#
#     props = {
#         "ApiKeyRequired": (bool, False),
#         "AuthorizationType": (basestring, False),
#         "AuthorizerId": (basestring, False),
#         #"HttpMethod": (basestring, False),
#         "Integration": (Integration, False),
#         "MethodResponses": ([MethodResponse], False),
#         "RequestModels": (dict, False),
#         "RequestParameters": (dict, False),
#         "ResourceId": (basestring, False),
#         #"RestApiId": (basestring, False)
#     }
