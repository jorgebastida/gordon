import os
import re
import json
from collections import defaultdict

import yaml
import boto3
import jinja2
import troposphere
from troposphere import iam, awslambda, s3

from . import exceptions
from . import utils
from . import actions
from . import resources


SETTINGS_FILE = 'settings.yml'

AVAILABLE_RESOURCES = {
    'lambdas': resources.lambdas.Lambda
}


def setup_region(region, settings=None):
    region = region or os.environ.get('AWS_DEFAULT_REGION', None) or (settings and settings.get('default-region', None)) or 'us-east-1'
    os.environ['AWS_DEFAULT_REGION'] = region
    return region


class Bootstrap(object):

    def __init__(self, path, **kwargs):
        self.path = path
        self.region = setup_region(kwargs.pop('region', None))
        self.project_name = kwargs.pop('project_name', None)
        self.app_name = kwargs.pop('app_name', None)
        self.runtime = kwargs.pop('runtime', None)
        self.root = os.path.dirname(os.path.abspath(__file__))

    def startproject(self):

        path = os.path.join(self.path, self.project_name)
        if os.path.exists(path):
            raise Exception("A directory with name {} already exists".format(self.project_name))
        else:
            os.makedirs(path)

        context = {
            'project_name': self.project_name,
            'default_region': self.region
        }

        self._clone_defaults(
            os.path.join(self.root, 'defaults', 'project'),
            path,
            context
        )

    def startapp(self):

        path = os.path.join(self.path, self.app_name)
        if os.path.exists(path):
            raise Exception("A directory with name {} already exists".format(self.app_name))
        else:
            os.makedirs(path)

        context = {
            'app_name': self.app_name,
        }

        self._clone_defaults(
            os.path.join(self.root, 'defaults', 'app_{}'.format(self.runtime)),
            path,
            context
        )

    def _clone_defaults(self, source, dest, context):
        for base, dirs, files in os.walk(source):

            relative = os.path.relpath(base, source)

            for d in dirs:
                os.makedirs(os.path.join(dest, relative, d))

            for filename in files:
                with open(os.path.join(base, filename), 'r') as f:
                    data = f.read()

                with open(os.path.join(dest, relative, filename), 'w') as f:
                    data = jinja2.Template(data).render(**context)
                    f.write(data)


class App(object):

    DEFAULT_SETTINS = {}

    def __init__(self, name, project, settings=None):
        self.name = name
        self.project = project
        self.settings = settings or {}
        self.path = os.path.join(self.project.path, name)
        self.settings = utils.load_settings(
            os.path.join(self.path, SETTINGS_FILE),
            default=self.DEFAULT_SETTINS
        )
        self._resources = defaultdict(list)
        self._load_resources()

    def _load_resources(self):
        for resource_type, resource_cls in AVAILABLE_RESOURCES.iteritems():
            for name in self.settings.get(resource_type, []):
                self._resources[resource_type].append(
                    resource_cls(
                        name=name,
                        app=self,
                        settings=self.settings.get(resource_type, {}).get(name)
                    )
                )

    def get_resources(self, resource_type):
        for r in self._resources[resource_type]:
            yield r


class Project(object):

    DEFAULT_SETTINS = {
        'apps': {}
    }

    def __init__(self, path, *args, **kwargs):
        self.path = path
        self.stage = kwargs.pop('stage', None)
        self.build_path = os.path.join(self.path, '_build')
        self.settings = utils.load_settings(
            os.path.join(self.path, SETTINGS_FILE),
            default=self.DEFAULT_SETTINS
        )
        self.name = self.settings['project']
        self.region = setup_region(kwargs.pop('region', None), self.settings)
        self.applications = []
        self._load_installed_applications()

    def _load_installed_applications(self):
        """Loads all installed applications."""
        for application in self.settings.get('apps', None) or []:
            if isinstance(application, basestring):
                application_name = application
                settings = {}
            elif isinstance(application, dict):
                application_name = application.keys()[0]
                settings = application.values()[0]
            else:
                raise exceptions.UnknownAppFormat(application)

            self.applications.append(
                App(
                    name=application_name,
                    settings=settings,
                    project=self
                )
            )

    def get_resources(self, resource_type):
        for application in self.applications:
            for r in application.get_resources(resource_type):
                yield r

    def build(self):
        if not os.path.exists(self.build_path):
            os.makedirs(self.build_path)

        self._reset_build_sequence_id()
        self._build_pre_project_template()
        self._build_project_template()
        self._build_pre_resources_template()
        self._build_resources_template()
        self._build_post_resources_template()

    def _reset_build_sequence_id(self):
        self._build_sequence = 0

    def _get_next_build_sequence_id(self):
        self._build_sequence += 1
        return "{:0>4}".format(self._build_sequence)

    def _base_troposphere_template(self):
        template = troposphere.Template()
        template.add_parameter(
            troposphere.Parameter(
                "Stage",
                Default="dev",
                Description="Name of the Stage",
                Type="String",
            )
        )

        template.add_parameter(
            troposphere.Parameter(
                "Region",
                Default="dev",
                Description="Name of the Stage",
                Type="String",
            )
        )
        return template

    def _build_pre_project_template(self, output_filename="{}_pre_project.json"):

        template = actions.ActionsTemplate()

        for resource_type, resource_cls in AVAILABLE_RESOURCES.iteritems():
            resource_cls.register_type_pre_project_template(self, template)
            for r in self.get_resources(resource_type):
                r.register_pre_project_template(template)

        if template:
            output_filename = output_filename.format(self._get_next_build_sequence_id())
            with open(os.path.join(self.build_path, output_filename), 'w') as f:
                f.write(template.to_json(indent=4))

    def _build_project_template(self,  output_filename="{}_project.json"):
        output_filename = output_filename.format(self._get_next_build_sequence_id())

        template = self._base_troposphere_template()

        for resource_type, resource_cls in AVAILABLE_RESOURCES.iteritems():
            resource_cls.register_type_project_template(self, template)
            for r in self.get_resources(resource_type):
                r.register_project_template(template)

        with open(os.path.join(self.build_path, output_filename), 'w') as f:
            f.write(template.to_json())

    def _build_pre_resources_template(self, output_filename="{}_pre_resources.json"):
        template = actions.ActionsTemplate()

        for resource_type, resource_cls in AVAILABLE_RESOURCES.iteritems():
            resource_cls.register_type_pre_resources_template(self, template)
            for r in self.get_resources(resource_type):
                r.register_pre_resources_template(template)

        if template:
            output_filename = output_filename.format(self._get_next_build_sequence_id())
            with open(os.path.join(self.build_path, output_filename), 'w') as f:
                f.write(template.to_json(indent=4))

    def _build_resources_template(self, output_filename="{}_resources.json"):

        template = self._base_troposphere_template()

        for resource_type, resource_cls in AVAILABLE_RESOURCES.iteritems():
            resource_cls.register_type_resources_template(self, template)
            for r in self.get_resources(resource_type):
                r.register_resources_template(template)

        if template:
            output_filename = output_filename.format(self._get_next_build_sequence_id())
            with open(os.path.join(self.build_path, output_filename), 'w') as f:
                f.write(template.to_json())

    def _build_post_resources_template(self, output_filename="{}_post_resources.json"):
        template = actions.ActionsTemplate()

        for resource_type, resource_cls in AVAILABLE_RESOURCES.iteritems():
            resource_cls.register_type_post_resources_template(self, template)
            for r in self.get_resources(resource_type):
                r.register_post_resources_template(template)

        if template:
            output_filename = output_filename.format(self._get_next_build_sequence_id())
            with open(os.path.join(self.build_path, output_filename), 'w') as f:
                f.write(template.to_json(indent=4))

    def apply(self):
        if not os.path.exists(self.build_path):
            raise Exception("It looks like you have not build this project.")

        steps = []
        for filename in os.listdir(self.build_path):
            match = re.match(r'(\d{4})_(.*)\.json', filename)
            if not match:
                continue

            with open(os.path.join(self.build_path, filename), 'r') as f:
                template = json.loads(f.read())
            template_type = 'custom' if '_type' in template else 'cf'
            steps.append((int(match.groups()[0]), match.groups()[1], filename, template_type))

            steps = sorted(steps, key=lambda x:x[0])

        context = {"Stage": self.stage}
        for (number, name, filename, template_type) in steps:
            getattr(self, 'apply_{}_template'.format(template_type))(name, filename, context)

    def apply_custom_template(self, name, filename, context):
        with open(os.path.join(self.build_path, filename), 'r') as f:
            template = actions.ActionsTemplate.from_dict(json.loads(f.read()))

        template.apply(context, self)


    def apply_cf_template(self, name, filename, context):
        stack_name = '-'.join([context['Stage'], self.name, name])
        stack = utils.create_or_update_cf_stack(
            name=stack_name,
            template_filename=os.path.join(self.build_path, filename),
            context=context
        )

        for output in stack.get('Outputs', []):
            context[output['OutputKey']] = output['OutputValue']
