from gordon.utils_tests import BaseIntegrationTest, BaseBuildTest
from gordon.utils import valid_cloudformation_name
from gordon import utils


class IntegrationTest(BaseIntegrationTest):

    def test_0001_project(self):
        self._test_project_step('0001_project')
        self.assert_stack_succeed('p')
        self.assert_stack_succeed('r')

        lambda_ = self.get_lambda(utils.valid_cloudformation_name('pyexample:pyexample'))
        self.assertEqual(lambda_['Runtime'], 'python2.7')
        self.assertEqual(lambda_['Description'], 'My description')
        self.assertEqual(lambda_['MemorySize'], 192)
        self.assertEqual(lambda_['Timeout'], 123)

        aliases = self.get_lambda_aliases(function_name=lambda_['FunctionName'])
        self.assertEqual(list(aliases.keys()), ['current'])

        response = self.invoke_lambda(
            function_name=lambda_['FunctionName'],
            payload={'key1': 'hello'}
        )
        self.assert_lambda_response(response, 'hello')


class BuildTest(BaseBuildTest):

    def test_0001_project(self):
        self._test_project_step('0001_project')
        self.assertBuild('0001_project', '0001_p.json')
        self.assertBuild('0001_project', '0002_pr_r.json')
        self.assertBuild('0001_project', '0003_r.json')

        self.assertRun(
            '0001_project',
            'pyexample.pyexample',
            '{"key1":"value1", "key2":"value2", "key3":"value3"}',
            ['Loading function',
            'value1 = value1',
            'output: value1',
            '']
        )
