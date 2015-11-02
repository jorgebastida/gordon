import os
import re
import json
import zipfile
import StringIO

import boto3
import troposphere
from troposphere import iam, awslambda, s3

from . import exceptions
from . import utils
from . import actions


SETTINGS_FILE = 'settings.yml'


class Lambda(object):

    PYTHON_2_7_RUNTIME = 'python2.7'
    NODEJS_0_10_36_RUNTIME = 'nodejs'
    JAVA_8_RUNTIME = 'python2.7'

    EXTENSIONS = {
        PYTHON_2_7_RUNTIME: 'py',
        NODEJS_0_10_36_RUNTIME: 'js',
        JAVA_8_RUNTIME: 'java',
    }

    def __init__(self, name, app_path, settings):
        self.name = name
        self.app_path = app_path
        self.settings = settings
        for key in ('code',):
            if key not in self.settings:
                raise Exception("Required setting {}".format(key))

    def get_runtime(self):
        """Return lambda runtime"""
        _, extension = os.path.splitext(self.settings.get('code'))

        if extension == '.py':
            return self.PYTHON_2_7_RUNTIME
        elif extension == '.js':
            return self.NODEJS_0_10_36_RUNTIME
        else:
            raise Exception('Unknown extension {}'.format(extension))

    def get_code(self):
        with open(os.path.join(self.app_path, self.settings['code']), 'r') as f:
            return f.read()

    def get_handler(self):
        return self.name

    def get_memory(self):
        """Returns the memory setting by rounding the actual value to the
        nearest power of 64. If no memory is defined, returns 128."""
        memory = int(self.settings.get('memory', 128))
        memory = memory + (64 - (memory % 64))
        return min(memory, 1536)

    def get_role(self):
        role = self.settings.get('role')
        if isinstance(role, basestring):
            return role
        elif role is None:
            policies = [iam.Policy(
                PolicyName=utils.valid_cloudformation_name(self.name, 'basic', 'policy'),
                PolicyDocument={
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents"
                            ],
                            "Resource": "arn:aws:logs:*:*:*",
                        }
                    ]
                }
            )]
        return iam.Role(
                utils.valid_cloudformation_name(self.name, 'role'),
                AssumeRolePolicyDocument={
                   "Version" : "2012-10-17",
                   "Statement": [ {
                      "Effect": "Allow",
                      "Principal": {
                         "Service": [ "ec2.amazonaws.com" ]
                      },
                      "Action": [ "sts:AssumeRole" ]
                   } ]
                },
                Policies=policies
            )


    def get_timeout(self):
        timeout = self.settings.get('timeout', 3)
        return max(min(timeout, 300), 1)

    def register_as_troposphere(self, template):
        role = self.get_role()
        if isinstance(role, iam.Role):
            template.add_resource(role)
            role = troposphere.GetAtt(role, 'Arn')

        template.add_resource(
            awslambda.Function(
                self.name,
                Code=awslambda.Code(
                    S3Bucket=troposphere.Ref("CodeBucket"),
                    S3Key=self.get_bucket_key(),
                    #S3ObjectVersion="",
                    #ZipFile="",
                ),
                Description=self.settings.get('description', ''),
                Handler=self.get_handler(),
                MemorySize=self.get_memory(),
                Role=role,
                Runtime=self.get_runtime(),
                Timeout=self.get_timeout()
            )
        )

    def get_bucket_key(self):
        return "{}.zip".format(self.name)

    def get_zip_file(self):
        filename = 'code.{}'.format(self.EXTENSIONS.get(self.get_runtime()))
        output = StringIO.StringIO()
        zipzile = zipfile.ZipFile(output, 'w')
        zipzile.write(os.path.join(self.app_path, self.settings['code']), filename)
        zipzile.close()
        output.seek(0)
        return output


class App(object):

    DEFAULT_SETTINS = {}

    def __init__(self, name, project_path, settings=None):
        self.name = name
        self.project_path = project_path
        self.settings = settings or {}
        self.path = os.path.join(self.project_path, name)
        self.settings = utils.load_settings(
            os.path.join(self.path, SETTINGS_FILE),
            default=self.DEFAULT_SETTINS
        )
        self.lambdas = []
        self._load_lambdas()

    def _load_lambdas(self):
        for name in self.settings.get('lambdas', []):
            self.lambdas.append(
                Lambda(
                    name=name,
                    app_path=self.path,
                    settings=self.settings.get('lambdas', {}).get(name)
                )
            )

    def get_lambdas(self):
        for _lambda in self.lambdas:
            yield _lambda


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
        self.applications = []
        self._load_installed_applications()

    def _load_installed_applications(self):
        """Loads all installed applications."""
        for application in self.settings.get('apps'):
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
                    project_path=self.path
                )
            )

    def get_lambdas(self):
        for application in self.applications:
            for _lambda in application.get_lambdas():
                yield _lambda

    def get_integrations(self):
        for application in self.applications:
            for integration in application.get_integrations():
                yield integration

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

        steps = sorted(steps, key=lambda x:x[1])

        context = {"Stage": self.stage}
        for (number, name, filename, template_type) in steps:
            getattr(self, 'apply_{}_template'.format(template_type))(name, filename, context)

    def apply_custom_template(self, name, filename, context):
        with open(filename, 'r') as f:
            template = json.loads(f.read())
        if template['_type'] == 'colle'

    def apply_cf_template(self, name, filename, context):
        stack_name = '-'.join([context['Stage'], self.name, name])
        stack = utils.create_or_update_cf_stack(
            name=stack_name,
            template_filename=os.path.join(self.build_path, filename),
            context=context
        )
        for output in stack['Outputs']:
            context[output['OutputKey']] = output['OutputValue']

    def build(self):
        if not os.path.exists(self.build_path):
            os.makedirs(self.build_path)

        self._build_project_template()
        self._build_code()
        self._build_resources_template()

    def _build_project_template(self):
        project_template = troposphere.Template()
        project_template.add_parameter(
            troposphere.Parameter(
                "Stage",
                Default="dev",
                Description="Name of the Stage",
                Type="String",
            )
        )

        code_bucket = s3.Bucket(
            "CodeBucket",
            BucketName=troposphere.Join('-', [troposphere.Ref("Stage"), self.name, 'piranha']),
            AccessControl=s3.Private,
        )
        project_template.add_resource(code_bucket)
        project_template.add_output([
            troposphere.Output(
                "CodeBucket",
                Description="CodeBucket name",
                Value=troposphere.Ref(code_bucket),
            )
        ])

        with open(os.path.join(self.build_path, '0001_project.json'), 'w') as f:
            f.write(project_template.to_json())

    def _build_resources_template(self):
        resources_template = troposphere.Template()

        resources_template.add_parameter(
            troposphere.Parameter(
                "CodeBucket",
                Description="Bucket where the code is located.",
                Type="String",
            )
        )

        for l in self.get_lambdas():
            l.register_as_troposphere(resources_template)

        with open(os.path.join(self.build_path, '0003_resources.json'), 'w') as f:
            f.write(resources_template.to_json())

    def _build_code(self):
        code_path = os.path.join(self.build_path, 'code')
        if not os.path.exists(code_path):
            os.makedirs(code_path)

        collection = actions.Collection()
        collection.add_parameter(
            name="CodeBucket",
        )

        for l in self.get_lambdas():
            filename = os.path.join(code_path, l.get_bucket_key())
            with open(filename, 'w') as f:
                f.write(l.get_zip_file().read())
                collection.add(
                    actions.UploadToS3(
                        bucket=actions.Ref('CodeBucket'),
                        key=l.get_bucket_key(),
                        filename=os.path.relpath(filename, self.build_path)
                    )
                )

        with open(os.path.join(self.build_path, '0002_upload_code.json'), 'w') as f:
            f.write(collection.to_json(indent=4))
