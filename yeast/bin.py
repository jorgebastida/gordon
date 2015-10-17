import os
import sys
import argparse

import boto3
from botocore.client import ClientError
from termcolor import colored

from . import exceptions
from .core import AWSLogs


__version__ = "0.0.1"


def main(argv=None):

    argv = (argv or sys.argv)[1:]

    parser = argparse.ArgumentParser(usage=("%(prog)s [ get | groups | streams ]"))

    subparsers = parser.add_subparsers()

    # get
    build_parser = subparsers.add_parser('build', description='Build')
    build_parser.set_defaults(func="build")

    # Parse input
    options, args = parser.parse_known_args(argv)

    try:
        logs = Yeast(**vars(options))
        getattr(logs, options.func)()
    except ClientError as exc:
        code = exc.response['Error']['Code']
        if code in (u'AccessDeniedException', u'ExpiredTokenException'):
            hint = exc.response['Error'].get('Message', 'AccessDeniedException')
            sys.stderr.write(colored("{0}\n".format(hint), "yellow"))
            return 4
        raise
    except exceptions.BaseAWSLogsException as exc:
        sys.stderr.write(colored("{0}\n".format(exc.hint()), "red"))
        return exc.code
    except Exception:
        import platform
        import traceback
        options = vars(options)
        options['aws_access_key_id'] = 'SENSITIVE'
        options['aws_secret_access_key'] = 'SENSITIVE'
        options['aws_session_token'] = 'SENSITIVE'
        sys.stderr.write("\n")
        sys.stderr.write("=" * 80)
        sys.stderr.write("\nYou've found a bug! Please, raise an issue attaching the following traceback\n")
        sys.stderr.write("https://github.com/jorgebastida/awslogs/issues/new\n")
        sys.stderr.write("-" * 80)
        sys.stderr.write("\n")
        sys.stderr.write("Version: {0}\n".format(__version__))
        sys.stderr.write("Python: {0}\n".format(sys.version))
        sys.stderr.write("boto3 version: {0}\n".format(boto3.__version__))
        sys.stderr.write("Platform: {0}\n".format(platform.platform()))
        sys.stderr.write("Config: {0}\n".format(options))
        sys.stderr.write("Args: {0}\n\n".format(sys.argv))
        sys.stderr.write(traceback.format_exc())
        sys.stderr.write("=" * 80)
        sys.stderr.write("\n")
        return 1

    return 0
