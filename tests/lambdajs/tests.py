import unittest

import boto3

from gordon.utils_tests import BaseIntegrationTest
from gordon.utils import valid_cloudformation_name


class IntegrationTest(BaseIntegrationTest, unittest.TestCase):

    def _test_apply(self):
        self.assert_stack_succeed('p')
        self.assert_stack_succeed('r')

        lambda_ = self.get_lambda(valid_cloudformation_name('jsexample:jsexample'))
        self.assertEqual(lambda_['Runtime'], 'nodejs4.3')
        self.assertEqual(lambda_['Description'], 'My description')
        self.assertEqual(lambda_['MemorySize'], 192)
        self.assertEqual(lambda_['Timeout'], 123)

        aliases = self.get_lambda_aliases(function_name=lambda_['FunctionName'])
        self.assertEqual(aliases.keys(), ['current'])

        response = self.invoke_lambda(
            function_name=lambda_['FunctionName'],
            payload={'key1': 'hello'}
        )
        self.assert_lambda_response(response, 'hello')
