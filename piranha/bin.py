import os
import sys
import argparse

import boto3
from botocore.client import ClientError
from termcolor import colored

from .core import Project

__version__ = "0.0.1"


def main(argv=None):

    argv = (argv or sys.argv)[1:]

    parser = argparse.ArgumentParser(usage=("%(prog)s [build]"))
    subparsers = parser.add_subparsers()

    build_parser = subparsers.add_parser('build', description='Build')
    build_parser.set_defaults(func="build")

    apply_parser = subparsers.add_parser('apply', description='Build')
    apply_parser.add_argument("-s", "--stage",
                            dest="stage",
                            type=str,
                            required=True,
                            help="Stage where to apply this project")

    apply_parser.set_defaults(func="apply")

    options, args = parser.parse_known_args(argv)

    path = os.getcwd()
    piranha = Project(path=path, **vars(options))
    getattr(piranha, options.func)()

    return 0
