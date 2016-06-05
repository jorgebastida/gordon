import os

from gordon.utils_tests import BaseIntegrationTest, BaseBuildTest
from gordon.utils import valid_cloudformation_name
from gordon import utils


class IntegrationTest(BaseIntegrationTest):

    def setUp(self):
        self.stream = self.create_kinesis_stream()
        self.extra_env['KINESIS_INTEGRATION'] = self.stream['StreamDescription']['StreamARN']
        super(IntegrationTest, self).setUp()

    def test_0001_project(self):
        self._test_project_step('0001_project')

        self.assert_stack_succeed('p')
        self.assert_stack_succeed('r')

        lambda_ = self.get_lambda(valid_cloudformation_name('kinesisconsumer:consumer'))
        self.assertEqual(lambda_['Runtime'], 'python2.7')

        aliases = self.get_lambda_aliases(function_name=lambda_['FunctionName'])
        self.assertEqual(list(aliases.keys()), ['current'])


class BuildTest(BaseBuildTest):

    def test_0001_project(self):
        self._test_project_step('0001_project')
        self.assertBuild('0001_project', '0001_p.json')
        self.assertBuild('0001_project', '0002_pr_r.json')
        self.assertBuild('0001_project', '0003_r.json')
