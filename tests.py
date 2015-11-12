import sys
import unittest
import urllib2

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

try:
    from mock import patch, Mock, call
except ImportError:
    from unittest.mock import patch, Mock, call


class TestGordon(unittest.TestCase):

    def test(self):
        return
