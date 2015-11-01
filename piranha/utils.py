import os
import re
import copy

import yaml


def load_settings(filename, default=None):
    """Returns a dictionary of the settings included in the YAML file
    called ``filename``. If the file is not present or empty, and empty
    dictionary is used. If ``default`` settings are preovided, those will be
    used as base."""
    settings = copy.copy(default)
    if not os.path.isfile(filename):
        custom_settings =  {}
    else:
        with open(filename, 'r') as f:
            custom_settings = yaml.load(f) or {}
    settings.update(custom_settings)
    return settings


def valid_cloudformation_name(*elements):
    elements = sum([re.split(r'[^a-zA-Z0-9]', e.title()) for e in elements], [])
    return ''.join(elements)
