import unittest

import boto3

from gordon.utils_tests import BaseIntegrationTest


class IntegrationTest(BaseIntegrationTest, unittest.TestCase):

    def _test_apply(self):
        self.assert_stack_succeed('project')
        self.assert_stack_succeed('resources')

        lambda_ = self.get_lambda('LambdaPyexamplePyexample')
        self.assertEqual(lambda_['Runtime'], 'python2.7')
        self.assertEqual(lambda_['Description'], 'My description')
        self.assertEqual(lambda_['MemorySize'], 192)
        self.assertEqual(lambda_['Timeout'], 123)

        aliases = self.get_lambda_aliases(function_name=lambda_['FunctionName'])
        self.assertEqual(aliases.keys(), ['Current'])

        response = self.invoke_lambda(
            function_name=lambda_['FunctionName'],
            payload={'key1': 'hello'}
        )
        self.assert_lambda_response(response, 'hello')
