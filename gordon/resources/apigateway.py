import re
from collections import defaultdict, Counter

import troposphere
from troposphere import sqs, sns, awslambda
from . import base
from gordon import exceptions
from gordon import utils
from gordon.contrib.apigateway import resources


class RestAPI(base.BaseResource):

    grn_type = 'api'

    def register_resources_template(self, template):
        template.add_resource(
            resources.APIGatewayRestAPI.create_with(
                self.in_project_cf_name,
                DependsOn=[self.project.reference('lambda:apigateway:rest_api')],
                lambda_arn=troposphere.GetAtt(
                    self.project.reference('lambda:apigateway:rest_api'), 'Arn'
                ),
                Name=self.name,
                Description=self.settings.get('description', '')
            )
        )


def append_slash(value):
    if not value or value[-1] != '/':
        return '{}/'.format(value)
    return value


class APIResource(base.BaseResource):

    grn_type = 'api-resource'

    required_settings = (
        'api',
    )

    def __init__(self, *args, **kwargs):
        self.api_name = kwargs['settings']['api']
        kwargs['name'] = append_slash(kwargs.pop('name'))

        if not isinstance(self.api_name, basestring):
            raise Exception()

        super(APIResource, self).__init__(*args, **kwargs)

    def get_path(self):
        return self.name.split('/', 2)[-2]

    def get_parent(self):
        parent_url_path = append_slash(self.name.rsplit('/', 3)[-3])
        if parent_url_path == '/':
            return parent_url_path
        return self.project.reference(
            'api-resource::{}:{}'.format(self.api_name, self._clean_grn_element(parent_url_path))
        )

    def get_api(self):
        return troposphere.GetAtt(
            self.project.reference('api::{}'.format(self.api_name)), 'Id'
        )

    def get_grn_path(self):
        return [self.api_name, self.name]

    def register_resources_template(self, template):
        template.add_resource(
            resources.APIGatewayResource.create_with(
                self.in_project_cf_name,
                DependsOn=[self.project.reference('lambda:apigateway:api_resource')],
                lambda_arn=troposphere.GetAtt(
                    self.project.reference('lambda:apigateway:api_resource'), 'Arn'
                ),
                RestApiId=self.get_api(),
                ParentId=self.get_parent(),
                PathPart=self.get_path(),
            )
        )
