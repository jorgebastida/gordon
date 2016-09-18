import os
import re
import sys
import argparse

from clint.textui import colored, puts

from .core import Bootstrap, ProjectBuild, ProjectApply, ProjectDelete, ProjectRun
from .exceptions import BaseGordonException


def stage_validator(s):
    """Stage names must be between 2 and 16 characters long."""
    if re.match(r'^[a-z0-9\-]{2,16}$', s):
        return s
    else:
        raise argparse.ArgumentTypeError("Stage names can only contain alphanumeric characters")


def main(argv=None, stdin=None):
    stdin = stdin or sys.stdin
    argv = (argv or sys.argv)[1:]

    parser = argparse.ArgumentParser()
    parser.format_usage = lambda: (
        "usage: gordon [%s]\n" % ' | '.join(parser._actions[1].choices.keys())
    )
    subparsers = parser.add_subparsers()

    def add_default_arguments(p):
        p.add_argument("--region",
                       dest="region",
                       help="AWS region where this project should be applied")

        p.add_argument("--debug",
                       dest="debug",
                       action="store_true",
                       help="Verbose output for debugging purpouses.")

    startproject_parser = subparsers.add_parser('startproject', description='Start a new project')
    add_default_arguments(startproject_parser)
    startproject_parser.set_defaults(cls=Bootstrap)
    startproject_parser.set_defaults(func="startproject")
    startproject_parser.add_argument("project_name",
                                     type=str,
                                     help="Name of the project.")

    startapp_parser = subparsers.add_parser('startapp', description='Start a new app')
    add_default_arguments(startapp_parser)
    startapp_parser.set_defaults(cls=Bootstrap)
    startapp_parser.set_defaults(func="startapp")
    startapp_parser.add_argument("app_name",
                                 type=str,
                                 help="Name of the application.")
    startapp_parser.add_argument("--runtime",
                                 dest="runtime",
                                 default='py',
                                 type=str,
                                 choices=('py', 'js', 'java'),
                                 help="App runtime")

    build_parser = subparsers.add_parser('build', description='Build')
    add_default_arguments(build_parser)
    build_parser.set_defaults(cls=ProjectBuild)
    build_parser.set_defaults(func="build")

    apply_parser = subparsers.add_parser('apply', description='Apply')
    add_default_arguments(apply_parser)
    apply_parser.set_defaults(cls=ProjectApply)
    apply_parser.set_defaults(func="apply")
    apply_parser.add_argument("-s", "--stage",
                              dest="stage",
                              type=stage_validator,
                              default='dev',
                              help="Stage where to apply this project")
    apply_parser.add_argument("--cf-timeout",
                              dest="timeout_in_minutes",
                              type=int,
                              default=15,
                              help="CloudFormation timeout.")

    run_parser = subparsers.add_parser('run', description='Run lambda locally')
    add_default_arguments(run_parser)
    run_parser.set_defaults(cls=ProjectRun)
    run_parser.set_defaults(func="run")
    run_parser.add_argument("lambda_name",
                            type=str,
                            help="Lambda you want to run locally in the format APP.LAMBDA_NAME")

    delete_parser = subparsers.add_parser('delete', description='Delete this project stacks')
    add_default_arguments(delete_parser)
    delete_parser.set_defaults(cls=ProjectDelete)
    delete_parser.set_defaults(func="delete")
    delete_parser.add_argument("-s", "--stage",
                               dest="stage",
                               type=str,
                               default='dev',
                               help="Stage where to apply this project")
    delete_parser.add_argument("--confirm",
                               dest="dry_run",
                               action="store_false",
                               help="Confirm the deletion of the resources")

    options, args = parser.parse_known_args(argv)

    path = os.getcwd()
    try:
        obj = options.cls(path=path, stdin=stdin, **vars(options))
        getattr(obj, options.func)()
    except BaseGordonException as exc:
        puts(colored.red("\n{}".format(exc.get_hint())))
        return exc.code
    except Exception:
        raise

    return 0
