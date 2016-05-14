import os

from gordon.utils_tests import BaseIntegrationTest, BaseBuildTest
from gordon import utils

class IntegrationTest(BaseIntegrationTest):

    def test_0001_project(self):
        self._test_project_step('0001_project')
        self.assert_stack_succeed('p')
        self.assert_stack_succeed('r')

        lambda_ = self.get_lambda(utils.valid_cloudformation_name('cron:example'))
        rule_ = self.get_rule(utils.valid_cloudformation_name('every_night_rule'))
        targets = self.get_rule_targets(rule_['Name'])
        self.assertEqual(rule_['ScheduleExpression'], 'cron(0 20 * * ? *)')
        self.assertEqual(len(targets), 1)
        self.assertEqual(targets[0]['Arn'], '{}:current'.format(lambda_['FunctionArn']))


class BuildTest(BaseBuildTest):

    def test_0001_project(self):
        self._test_project_step('0001_project')
        self.assertBuild('0001_project', '0001_p.json')
        self.assertBuild('0001_project', '0002_pr_r.json')
        self.assertBuild('0001_project', '0003_r.json')
