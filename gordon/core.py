# -*- coding: utf-8 -*-
import os
import re
import json
import copy
import shutil
from collections import defaultdict

import yaml
import boto3
import jinja2
import troposphere
from troposphere import iam, awslambda, s3
from clint.textui import colored, puts, progress, indent

from . import exceptions
from . import utils
from . import actions
from . import resources
from . import protocols

SETTINGS_FILE = 'settings.yml'

AVAILABLE_RESOURCES = {
    'lambdas': resources.lambdas.Lambda,
    'dynamodb': resources.dynamodb.Dynamodb,
    'kinesis': resources.kinesis.Kinesis,
    's3': resources.s3.BucketNotificationConfiguration
}


class BaseResourceContainer(object):
    """Base abstraction about types which can define resources in their settings."""

    def __init__(self, *args, **kwargs):
        self._resources = defaultdict(list)
        self._load_resources()

    def _load_resources(self):
        """Load resources defined in ``self.settings`` and stores them in
        ``self._resources`` map."""
        for resource_type, resource_cls in AVAILABLE_RESOURCES.iteritems():
            for name in self.settings.get(resource_type, {}):
                extra = {
                    'project': getattr(self, 'project', None) or self,
                    'app': self if hasattr(self, 'project') else None,
                }

                with indent(4 if hasattr(self, 'project') else 2):
                    puts(colored.green(u"✓ {}".format(name)))

                self._resources[resource_type].append(
                    resource_cls.factory(
                        name=name,
                        settings=self.settings.get(resource_type, {})[name],
                        **extra
                    )
                )

    def get_resources(self, resource_type):
        for r in self._resources[resource_type]:
            yield r


class App(BaseResourceContainer):
    """Container of resources of the same domain."""

    DEFAULT_SETTINS = {}

    def __init__(self, name, project, path=None, settings=None, *args, **kwargs):
        self.name = name
        self.project = project
        self.path = path or os.path.join(self.project.path, name)
        self.settings = utils.load_settings(
            os.path.join(self.path, SETTINGS_FILE),
            default=self.DEFAULT_SETTINS,
            protocols=protocols.BASE_BUILD_PROTOCOLS
        )
        self.settings.update(settings or {})
        super(App, self).__init__(*args, **kwargs)


class BaseProject(object):
    """Base Project representation accross different actions."""

    DEFAULT_SETTINS = {}

    def __init__(self, path, *args, **kwargs):
        self.path = path
        self.debug = kwargs.pop('debug', False)
        self.build_path = os.path.join(self.path, '_build')
        self.root = os.path.dirname(os.path.abspath(__file__))
        self.settings = utils.load_settings(
            os.path.join(self.path, SETTINGS_FILE),
            default=self.DEFAULT_SETTINS,
            protocols=protocols.BASE_BUILD_PROTOCOLS
        )
        self.name = self.settings['project']


class ProjectBuild(BaseProject, BaseResourceContainer):
    """Representation of a project on build time. This type initializes
    application and resources defined accrross the settings."""

    DEFAULT_SETTINS = {
        'apps': {}
    }

    def __init__(self, *args, **kwargs):
        self.applications = []
        self._in_project_resource_references = {}
        BaseProject.__init__(self, *args, **kwargs)
        puts(colored.blue("Loading project resources"))
        BaseResourceContainer.__init__(self, *args, **kwargs)
        puts(colored.blue("Loading installed applications"))
        self._load_installed_applications()

    def _load_installed_applications(self):
        """Loads all installed applications.
        Applications can be defined as string or dictionaries.
        - If applications are strings, gordon assume the application is located
        within your project root. There is only one exception to this rule.
        If the application name starts with ``gordon.contrib.`` gordon will
        assume the code of the app resides within the gordon package.
        It would be really nice if apps were simple python modules, but we
        can't assume that as lambdas can be created with several runtimes,
        and people from really different backgrounds (without much idea of
        python - if any) should feel confortable using this tool.
        - If your applcation os defined as a dicctionary, the first key is
        assumed to be the name and the value of that key is assumed to be a
        settings dictionary that will override the default app settings.
        """
        for application in self.settings.get('apps', None) or []:
            path = None
            if isinstance(application, basestring):
                if application.startswith('gordon.contrib.'):
                    application = application[len('gordon.contrib.'):]
                    path = os.path.join(self.root, 'contrib', application)
                application_name = application
                settings = {}
            elif isinstance(application, dict):
                application_name = application.keys()[0]
                settings = application.values()[0]
            else:
                raise exceptions.InvalidAppFormatError(application)

            with indent(2):
                puts(colored.cyan("{}:".format(application_name)))

            self.applications.append(
                App(
                    name=application_name,
                    settings=settings,
                    project=self,
                    path=path
                )
            )

    def register_resource_reference(self, name, cf_name):
        """Register a resouce called ``name`` as ``cf_name``"""
        if name in self._in_project_resource_references or \
           cf_name in self._in_project_resource_references.values():
            raise exceptions.DuplicateResourceNameError(name, cf_name)

        self._in_project_resource_references[name] = cf_name

    def reference(self, name):
        """Resolve ``name`` as a CloudFormation reference"""
        if name in self._in_project_resource_references:
            return self._in_project_resource_references[name]
        raise KeyError(name, self._in_project_resource_references.keys())

    def get_resources(self, resource_type):
        """Returns all project and application resources"""
        for application in self.applications:
            for r in application.get_resources(resource_type):
                yield r

        for r in BaseResourceContainer.get_resources(self, resource_type):
            yield r

    def build(self):
        """Build current current project"""
        puts(colored.blue("Building project..."))

        if os.path.exists(self.build_path):
            shutil.rmtree(self.build_path)
        os.makedirs(self.build_path)

        with indent(2):
            self._reset_build_sequence_id()
            self._build_pre_project_template()
            self._build_project_template()
            self._build_pre_resources_template()
            self._build_resources_template()
            self._build_post_resources_template()

    def _reset_build_sequence_id(self):
        self._build_sequence = 0

    def _get_next_build_sequence_id(self):
        """Return next build sequence id"""
        self._build_sequence += 1
        return "{:0>4}".format(self._build_sequence)

    def _base_troposphere_template(self):
        """Returns the most basic troposphere template possible"""
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
                Description="Name of the Stage",
                Type="String",
            )
        )
        return template

    def _build_pre_project_template(self, output_filename="{}_pr_p.json"):
        """Collect registered hooks both for ``register_type_pre_project_template``
        and ``register_pre_project_template``"""
        template = actions.ActionsTemplate()

        for resource_type, resource_cls in AVAILABLE_RESOURCES.iteritems():
            resource_cls.register_type_pre_project_template(self, template)
            for r in self.get_resources(resource_type):
                r.register_pre_project_template(template)

        if template:
            output_filename = output_filename.format(self._get_next_build_sequence_id())
            puts(colored.green(u"✓ {}".format(output_filename)))
            with open(os.path.join(self.build_path, output_filename), 'w') as f:
                f.write(template.to_json(indent=4))

    def _build_project_template(self,  output_filename="{}_p.json"):
        """Collect registered hooks both for ``register_type_project_template``
        and ``register_project_template``"""

        output_filename = output_filename.format(self._get_next_build_sequence_id())
        template = self._base_troposphere_template()

        for resource_type, resource_cls in AVAILABLE_RESOURCES.iteritems():
            resource_cls.register_type_project_template(self, template)
            for r in self.get_resources(resource_type):
                r.register_project_template(template)

        template = utils.fix_troposphere_references(template)

        puts(colored.green(u"✓ {}".format(output_filename)))
        with open(os.path.join(self.build_path, output_filename), 'w') as f:
            f.write(template.to_json())

    def _build_pre_resources_template(self, output_filename="{}_pr_r.json"):
        """Collect registered hooks both for ``register_type_pre_resources_template``
        and ``register_pre_resources_template``"""
        template = actions.ActionsTemplate()

        for resource_type, resource_cls in AVAILABLE_RESOURCES.iteritems():
            resource_cls.register_type_pre_resources_template(self, template)
            for r in self.get_resources(resource_type):
                r.register_pre_resources_template(template)

        if template:
            output_filename = output_filename.format(self._get_next_build_sequence_id())
            puts(colored.green(u"✓ {}".format(output_filename)))
            with open(os.path.join(self.build_path, output_filename), 'w') as f:
                f.write(template.to_json(indent=4))

    def _build_resources_template(self, output_filename="{}_r.json"):
        """Collect registered hooks both for ``register_type_resources_template``
        and ``register_resources_template``"""

        template = self._base_troposphere_template()

        for resource_type, resource_cls in AVAILABLE_RESOURCES.iteritems():
            resource_cls.register_type_resources_template(self, template)
            for r in self.get_resources(resource_type):
                r.register_resources_template(template)

        template = utils.fix_troposphere_references(template)

        if template and template.resources:
            output_filename = output_filename.format(self._get_next_build_sequence_id())
            puts(colored.green(u"✓ {}".format(output_filename)))
            with open(os.path.join(self.build_path, output_filename), 'w') as f:
                f.write(template.to_json())

    def _build_post_resources_template(self, output_filename="{}_ps_r.json"):
        """Collect registered hooks both for ``register_type_post_resources_template``
        and ``register_post_resources_template``"""

        template = actions.ActionsTemplate()

        for resource_type, resource_cls in AVAILABLE_RESOURCES.iteritems():
            resource_cls.register_type_post_resources_template(self, template)
            for r in self.get_resources(resource_type):
                r.register_post_resources_template(template)

        if template:
            output_filename = output_filename.format(self._get_next_build_sequence_id())
            puts(colored.green(u"✓ {}".format(output_filename)))
            with open(os.path.join(self.build_path, output_filename), 'w') as f:
                f.write(template.to_json(indent=4))


class ProjectApply(BaseProject):
    """Representation of a project on apply time."""

    def __init__(self, *args, **kwargs):
        super(ProjectApply, self).__init__(*args, **kwargs)
        self.stage = kwargs.pop('stage', None)
        self.region = utils.setup_region(kwargs.pop('region', None), self.settings)

    def apply(self):
        """Loop all over the .json files in the build folder and apply each of
        them. Use the output of each of them to populate the context of the
        subsequent templates."""

        puts(colored.blue("Applying project..."))

        if not os.path.exists(self.build_path):
            raise exceptions.ProjectNotBuildError()

        steps = []
        for filename in os.listdir(self.build_path):
            match = re.match(r'(\d{4})_(.*)\.json', filename)
            if not match:
                continue

            with open(os.path.join(self.build_path, filename), 'r') as f:
                template = json.loads(f.read())

            template_type = 'custom' if '_type' in template else 'cloudformation'
            steps.append((int(match.groups()[0]), match.groups()[1], filename, template_type))
            steps = sorted(steps, key=lambda x:x[0])

        context = {"Stage": self.stage, 'Region': self.region}
        context.update(self.collect_parameters())

        for (number, name, filename, template_type) in steps:
            with indent(2):
                puts(colored.cyan("{} ({})".format(filename, template_type)))
            with indent(4):
                if self.debug:
                    puts(colored.yellow(u"✸ Applying template {} with context {}".format(filename, context)))
                getattr(self, 'apply_{}_template'.format(template_type))(name, filename, context)

    def collect_parameters(self):
        """Collect parameters from both the ``common.yml`` parameters file and
        the specific parameters file for the selected stage."""

        parameters = {}
        parameters_paths = (
            os.path.join(self.path, 'parameters', 'common.yml'),
            os.path.join(self.path, 'parameters', '{}.yml'.format(self.stage)),
        )

        context = {
            'stage': self.stage,
            'aws_region': self.region,
            'aws_account_id': boto3.client('iam').get_user()['User']['Arn'].split(':')[4],
            'env': os.environ
        }

        for path in parameters_paths:
            if os.path.exists(path):
                params = utils.load_settings(
                    path,
                    jinja2_enrich=True,
                    protocols=protocols.BASE_APPLY_PROTOCOLS,
                    context=context
                )
                parameters.update(params)

        return parameters

    def apply_custom_template(self, name, filename, context):
        """Apply ``filename`` template with ``context``-"""
        with open(os.path.join(self.build_path, filename), 'r') as f:
            template = actions.ActionsTemplate.from_dict(json.loads(f.read()))

        outputs = template.apply(context, self)

        for key, value in outputs.iteritems():
            context[key] = value

    def apply_cloudformation_template(self, name, filename, context):
        """Apply ``filename`` template with ``context``-"""
        stack_name = utils.generate_stack_name(context['Stage'], self.name, name)
        stack = utils.create_or_update_cf_stack(
            name=stack_name,
            template_filename=os.path.join(self.build_path, filename),
            context=context
        )

        for output in stack.get('Outputs', []):
            context[output['OutputKey']] = output['OutputValue']


class Bootstrap(object):
    """Project and apps bootstraper"""

    def __init__(self, path, **kwargs):
        self.path = path
        self.region = utils.setup_region(kwargs.pop('region', None))
        self.project_name = kwargs.pop('project_name', None)
        self.app_name = kwargs.pop('app_name', None)
        self.runtime = kwargs.pop('runtime', None)
        self.root = os.path.dirname(os.path.abspath(__file__))

    def startproject(self):
        """Create a new project called ``project_name``."""

        path = os.path.join(self.path, self.project_name)
        if os.path.exists(path):
            raise exceptions.ProjectDirectoryAlreadyExistsError(self.project_name)
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
        """Create a new application called ``app_name``."""

        path = os.path.join(self.path, self.app_name)
        if os.path.exists(path):
            raise exceptions.AppDirectoryAlreadyExistsError(self.app_name)
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
        """Clone ``source`` directory into ``dest`` directory and enrich
        files assuming they are jinja2 templates"""

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
