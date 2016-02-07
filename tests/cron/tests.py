import unittest

from gordon.utils_tests import BaseIntegrationTest
from gordon import utils


class IntegrationTest(BaseIntegrationTest, unittest.TestCase):

    def _test_apply(self):
        self.assert_stack_succeed('p')
        self.assert_stack_succeed('r')

        lambda_ = self.get_lambda(utils.valid_cloudformation_name('cron:example'))
        rule_ = self.get_rule(utils.valid_cloudformation_name('every_night_rule'))
        targets = self.get_rule_targets(rule_['Name'])
        self.assertEqual(rule_['ScheduleExpression'], 'cron(0 20 * * ? *)')
        self.assertEqual(len(targets), 1)
        self.assertEqual(targets[0]['Arn'], '{}:current'.format(lambda_['FunctionArn']))
