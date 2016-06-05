import os
import json

import boto3
import requests

from gordon.utils_tests import BaseIntegrationTest, BaseBuildTest
from gordon.utils import valid_cloudformation_name
from gordon import utils


class IntegrationTest(BaseIntegrationTest):

    def test_0001_project(self):
        self._test_project_step('0001_project')
        self.assert_stack_succeed('p')
        self.assert_stack_succeed('r')

        lambda_ = self.get_lambda(utils.valid_cloudformation_name('pyexample:hellopy'))
        self.assertEqual(lambda_['Runtime'], 'python2.7')
        self.assertEqual(lambda_['Description'], 'My hello description')
        self.assertEqual(lambda_['MemorySize'], 192)
        self.assertEqual(lambda_['Timeout'], 123)

        aliases = self.get_lambda_aliases(function_name=lambda_['FunctionName'])
        self.assertEqual(list(aliases.keys()), ['current'])

        response = self.invoke_lambda(
            function_name=lambda_['FunctionName'],
            payload={}
        )
        self.assert_lambda_response(response, 'hello')

        lambda_ = self.get_lambda(utils.valid_cloudformation_name('pyexample:byepy'))
        self.assertEqual(lambda_['Runtime'], 'python2.7')
        self.assertEqual(lambda_['Description'], 'My bye description')
        self.assertEqual(lambda_['MemorySize'], 192)
        self.assertEqual(lambda_['Timeout'], 123)

        aliases = self.get_lambda_aliases(function_name=lambda_['FunctionName'])
        self.assertEqual(list(aliases.keys()), ['current'])

        response = self.invoke_lambda(
            function_name=lambda_['FunctionName'],
            payload={}
        )
        self.assert_lambda_response(response, 'bye')

        client = boto3.client('apigateway')
        api = [a for a in client.get_rest_apis()['items'] if a['name'] == 'helloapi-{}'.format(self.uid)][0]
        endpoint = 'https://{}.execute-api.{}.amazonaws.com/{}'.format(api['id'], os.environ['AWS_DEFAULT_REGION'], self.uid)

        response = requests.get(endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), '"hello"')

        response = requests.get('{}/404'.format(endpoint))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content.decode('utf-8'), '"hello"')

        response = requests.get('{}/shop/2'.format(endpoint))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), '"hello"')

        response = requests.get('{}/http'.format(endpoint))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content.decode('utf-8'))['args'], {'hello': 'world'})

        response = requests.get('{}/complex'.format(endpoint))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), '"hello"')

        response = requests.post('{}/complex'.format(endpoint))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), '"bye"')


class BuildTest(BaseBuildTest):

    def test_0001_project(self):
        self.maxDiff = None
        self._test_project_step('0001_project')
        self.assertBuild('0001_project', '0001_p.json')
        self.assertBuild('0001_project', '0002_pr_r.json')
        self.assertBuild('0001_project', '0003_r.json')
