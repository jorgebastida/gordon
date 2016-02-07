import unittest

from gordon.utils_tests import BaseIntegrationTest
from gordon.utils import valid_cloudformation_name


class IntegrationTest(BaseIntegrationTest, unittest.TestCase):

    def setUp(self):
        self.stream = self.create_kinesis_stream()
        self.extra_env['KINESIS_INTEGRATION'] = self.stream['StreamDescription']['StreamARN']
        super(IntegrationTest, self).setUp()

    def _test_apply(self):
        self.assert_stack_succeed('p')
        self.assert_stack_succeed('r')

        lambda_ = self.get_lambda(valid_cloudformation_name('kinesisconsumer:consumer'))
        self.assertEqual(lambda_['Runtime'], 'python2.7')

        aliases = self.get_lambda_aliases(function_name=lambda_['FunctionName'])
        self.assertEqual(aliases.keys(), ['current'])
