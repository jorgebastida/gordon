import unittest
from gordon.utils_tests import BaseIntegrationTest


class IntegrationTest(BaseIntegrationTest, unittest.TestCase):

    def _test_apply(self):
        self.assert_stack_succeed('p')
        self.assert_stack_succeed('r')
