import sys
import unittest
import urllib2

try:
    from mock import patch, Mock, call
except ImportError:
    from unittest.mock import patch, Mock, call

from gordon.actions import Parameter, ActionsTemplate, GetAttr
from gordon import exceptions


class TestActions(unittest.TestCase):

    def test_basic_serializable(self):

        t = Parameter(name="Name", default="Default")
        s = t.serialize()
        self.assertEqual(s, {'_type': 'Parameter', 'name': 'Name', 'default': 'Default'})
        self.assertEqual(t, Parameter.from_dict(s))

        t = Parameter(name="Name")
        s = t.serialize()
        self.assertEqual(s, {'_type': 'Parameter', 'name': 'Name', 'default': ''})
        self.assertEqual(t, Parameter.from_dict(s))

        self.assertRaises(exceptions.PropertyRequiredError, Parameter)

    def test_complex_serializable(self):

        t = ActionsTemplate()
        s = t.serialize()
        self.assertEqual(s, {'_type': 'ActionsTemplate', 'actions': [], 'parameters': {}, 'outputs': {}, 'parallelizable': False})
        self.assertEqual(t, ActionsTemplate.from_dict(s))

    def test_actions_template(self):
        context, project = Mock(), Mock()
        action = Mock()
        action.name = 'upload'
        action.apply.return_value = {'version': '1234'}

        parameter = Mock()
        parameter.name = "name"

        output = Mock()
        output.name = "version"
        output.value = GetAttr(action='upload', attr='version')
        output2 = Mock()
        output2.name = "pi"
        output2.value = "3.1416"

        at = ActionsTemplate()
        at.add(action)
        at.add_parameter(parameter)
        at.add_output(output)
        at.add_output(output2)

        self.assertEqual(at.apply(context, project), {'version': '1234', 'pi': '3.1416'})



        # action_outputs = {}
        # for action in self.actions:
        #     action_outputs[action.name] = action.apply(context, project)
        #
        # outputs = {}
        # for name, output in self.outputs.iteritems():
        #     if isinstance(output.value, GetAttr):
        #         value = action_outputs[output.value.action].get(output.value.attr, output.default)
        #     outputs[name] = value
        # return outputs
