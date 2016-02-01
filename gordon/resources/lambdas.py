# -*- coding: utf-8 -*-
import os
import shutil
import tempfile
import hashlib
import zipfile
import StringIO
import json
import subprocess

import troposphere
from troposphere import iam, awslambda, s3
from clint.textui import colored, puts, indent

from gordon import actions
from gordon import utils
from gordon import exceptions
from gordon.contrib.lambdas.resources import LambdaVersion, LambdaAlias
from . import base


class Lambda(base.BaseResource):
    """Base Lambda Resource which defines all shared resources between
    runtimes.
    """

    REQUIRED_SETTINGS = ('code', )
    code_filename = 'code'
    grn_type = 'lambda'

    @classmethod
    def factory(cls, *args, **kwargs):
        """Returns an instance of one of the severeal available Lambda
        resources based on the runtime."""
        _, extension = os.path.splitext(kwargs['settings']['code'])
        runtime = kwargs['settings'].get('runtime', None)

        if runtime == 'python' or extension == '.py':
            return PythonLambda(*args, **kwargs)
        elif runtime == 'javascript' or extension == '.js':
            return NodeLambda(*args, **kwargs)
        elif runtime == 'java':
            return JavaLambda(*args, **kwargs)
        else:
            raise exceptions.InvalidLambdaCodeExtensionError(extension)

    def __init__(self, *args, **kwargs):
        super(Lambda, self).__init__(*args, **kwargs)

        self.current_alias_project_name = '{}:current'.format(self.in_project_name)
        self.current_alias_cf_name = utils.valid_cloudformation_name(self.name, "CurrentAlias")

        self.project.register_resource_reference(
            self.current_alias_project_name,
            self.current_alias_cf_name
        )

    def get_handler(self):
        """Returns the name of the handler. If there is no any available in
        the settngs we assume is ``handler``."""
        return self.settings.get('handler', '{}.handler'.format(self.code_filename))

    def get_memory(self):
        """Returns the memory setting by rounding the actual value to the
        nearest multiple of 64. If no memory is defined, returns 128."""
        memory = int(self.settings.get('memory', 128))
        memory = memory - (memory % 64)
        return min(memory, 1536)

    def get_timeout(self):
        """Returns the timeout value for this lambda."""
        timeout = self.settings.get('timeout', 3)
        return max(min(timeout, 300), 1)

    def _get_policies(self):
        """Returns a list of policies to attach to the IAM Role of this Lambda.
        Users can add more policies to this Role by defining policy documents
        in the settings of the lambda under the ``policies`` key."""

        policies = [
            iam.Policy(
                PolicyName=utils.valid_cloudformation_name(self.name, 'logs', 'policy'),
                PolicyDocument={
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "lambda:InvokeFunction"
                            ],
                            "Resource": [
                                "*"
                            ]
                        },
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
            ),
        ]

        for policy_nme, policy_document in self.settings.get('policies', {}).iteritems():
            policies.append(
                iam.Policy(
                    PolicyName=utils.valid_cloudformation_name(self.name, policy_nme, 'policy'),
                    PolicyDocument=policy_document
                )
            )
        return policies

    def get_role(self):
        """Returns the role this lambda function will use. Users can customize
        which role to apply by referencing the ARN of the role. If no Role
        is defined, gordon will create and assing one with the basic
        permissions suggested by AWS.

        Users can customize the policies attached to the role using
        ``policies`` in the lambda settings."""

        role = self.settings.get('role')

        if isinstance(role, basestring):
            return role
        elif role is None:
            pass
        else:
            raise exceptions.InvalidLambdaRoleError(self.name, role)

        return iam.Role(
            utils.valid_cloudformation_name(self.name, 'role'),
                AssumeRolePolicyDocument={
                   "Version" : "2012-10-17",
                   "Statement": [ {
                      "Effect": "Allow",
                      "Principal": {
                         "Service": [ "lambda.amazonaws.com" ]
                      },
                      "Action": [ "sts:AssumeRole" ]
                   } ]
                },
                Policies=self._get_policies()
        )

    def get_bucket_key(self):
        """Return the S3 bucket key for this lambda."""
        filename = '_'.join(self.in_project_name.split(':')[1:])
        return "{}.zip".format(filename)

    @classmethod
    def register_type_project_template(cls, project, template):
        """Registers into the project stack a S3 bucket where all lambdas
        code will be stored, as well as an output so any subsequent template
        can have a reference to this resource."""

        code_bucket = s3.Bucket(
            "CodeBucket",
            BucketName=project.settings['code-bucket'],
            AccessControl=s3.Private,
            VersioningConfiguration=s3.VersioningConfiguration(
                Status='Enabled'
            )
        )
        template.add_resource(code_bucket)
        template.add_output([
            troposphere.Output(
                "CodeBucket",
                Description="CodeBucket name",
                Value=project.settings['code-bucket'],
            )
        ])

    @classmethod
    def register_type_resources_template(cls, project, template):
        """Registers into the resources stack ``CodeBucket`` as parameter
        so any resource in the template can use it."""
        template.add_parameter(
            troposphere.Parameter(
                "CodeBucket",
                Description="Bucket where the code is located.",
                Type="String",
            )
        )

    def register_resources_template(self, template):
        """Register the lambda Function into the troposphere template. If
        this function requires a custom Role, register it too."""

        role = self.get_role()
        depends_on = []
        if isinstance(role, iam.Role):
            template.add_resource(role)
            depends_on.append(role.name)
            role = troposphere.GetAtt(role, 'Arn')

        template.add_parameter(
            troposphere.Parameter(
                utils.valid_cloudformation_name(self.name, "s3version"),
                Type="String",
            )
        )

        function = template.add_resource(
            awslambda.Function(
                self.in_project_cf_name,
                DependsOn=depends_on,
                Code=awslambda.Code(
                    S3Bucket=troposphere.Ref("CodeBucket"),
                    S3Key=self.get_bucket_key(),
                    S3ObjectVersion=troposphere.Ref(
                        utils.valid_cloudformation_name(self.name, "s3version")
                    ),
                ),
                Description=self.settings.get('description', ''),
                Handler=self.get_handler(),
                MemorySize=self.get_memory(),
                Role=role,
                Runtime=self.runtime,
                Timeout=self.get_timeout()
            )
        )

        lambda_version = 'lambda:contrib_lambdas:version'
        if not self.in_project_name.startswith('lambda:contrib_lambdas:'):
            lambda_version = '{}:current'.format(lambda_version)

        version = template.add_resource(
            LambdaVersion.create_with(
                utils.valid_cloudformation_name(self.name, "Version"),
                DependsOn=[self.project.reference(lambda_version)],
                lambda_arn=troposphere.GetAtt(
                    self.project.reference(lambda_version), 'Arn'
                ),
                FunctionName=troposphere.Ref(
                    function
                ),
                S3ObjectVersion=troposphere.Ref(
                    utils.valid_cloudformation_name(self.name, "s3version")
                ),
            )
        )

        lambda_alias = 'lambda:contrib_lambdas:alias'
        if not self.in_project_name.startswith('lambda:contrib_lambdas:'):
            lambda_alias = '{}:current'.format(lambda_alias)

        template.add_resource(
            LambdaAlias.create_with(
                self.current_alias_cf_name,
                DependsOn=[self.project.reference(lambda_alias)],
                lambda_arn=troposphere.GetAtt(
                    self.project.reference(lambda_alias), 'Arn'
                ),
                FunctionName=troposphere.Ref(
                    function
                ),
                S3ObjectVersion=troposphere.Ref(
                    utils.valid_cloudformation_name(self.name, "s3version")
                ),
                FunctionVersion=troposphere.GetAtt(
                    version, "Version"
                ),
                Name="current",
            )
        )

    def register_pre_resources_template(self, template):
        """Register one UploadToS3 action into the pre_resources template, as
        well as several Outputs so subsequente templates can reference these
        files.
        Before registering these actions, we create the .zip file we'll
        upload to s3 on apply time.
        """

        code_path = os.path.join(self.project.build_path, 'code')
        if not os.path.exists(code_path):
            os.makedirs(code_path)

        # We need to know to which bucket we are uploading these files.
        template.add_parameter(
            actions.Parameter(
                name="CodeBucket"
            )
        )

        filename = os.path.join(code_path, self.get_bucket_key())
        with open(filename, 'w') as f:
            f.write(self.get_zip_file().read())

        template.add(
            actions.UploadToS3(
                name="{}-upload".format(self.name),
                bucket=actions.Ref(name='CodeBucket'),
                key=self.get_bucket_key(),
                filename=os.path.relpath(filename, self.project.build_path)
            )
        )
        template.add_output(
            actions.Output(
                name=utils.valid_cloudformation_name(self.name, "s3url"),
                value=actions.GetAttr(
                    action="{}-upload".format(self.name),
                    attr="s3url",
                )
            )
        )
        template.add_output(
            actions.Output(
                name=utils.valid_cloudformation_name(self.name, "s3version"),
                value=actions.GetAttr(
                    action="{}-upload".format(self.name),
                    attr="s3version",
                )
            )
        )

    def get_zip_file(self):
        """Returns a zip file file-like object with all the required source
        on it."""
        destination = tempfile.mkdtemp()
        digest = hashlib.sha1()

        with indent(2):
            puts(colored.green(u"✓ {}".format(self._get_in_project_name())))

        try:
            self._collect_lambda_content(destination)
        except subprocess.CalledProcessError, exc:
            raise exceptions.LambdaBuildProcessError(exc, self)

        output = StringIO.StringIO()
        zf = zipfile.ZipFile(output, 'w')

        for base, dirs, files in os.walk(destination):
            relative = os.path.relpath(base, destination)

            for filename in files:
                source = os.path.join(destination, base, filename)
                relative_destination = os.path.join(relative, filename)
                zf.write(source, relative_destination)
                with open(source, 'rb') as f:
                    digest.update(f.read())

        # Calculate digest of destination
        metadata = {'sha1': digest.hexdigest()}
        zf.writestr('.metadata', json.dumps(metadata))

        zf.close()
        output.seek(0)
        shutil.rmtree(destination)
        return output

    def _collect_lambda_file_content(self, destination):
        filename = '{}.{}'.format(self.code_filename, self.extension)
        shutil.copyfile(os.path.join(self.get_root(), self.settings['code']), os.path.join(destination, filename))

    def _collect_lambda_module_content(self, destination):
        root = os.path.join(self.get_root(), self.settings['code'])
        for base, dirs, files in os.walk(root):
            relative = os.path.relpath(base, root)
            for filename in files:
                relative_destination = os.path.join(relative, filename)
                shutil.copyfile(os.path.join(base, filename), os.path.join(destination, relative_destination))

    def collect_lambda_content(self):
        """Collects all required files to be included in the .zip file of the
        lambda. Returns a temporal directory path
        """
        raise NotImplementedError


class PythonLambda(Lambda):

    runtime = 'python2.7'
    base_runtime = 'python'
    extension = 'py'

    def _pip_path(self):
        return self.project.settings.get('pip-path', 'pip')

    def _pip_extra(self):
        extra = (
            self.project.settings.get('pip-extra'),
            self.app and self.app.settings.get('pip-extra'),
            self.settings.get('pip-extra'),
        )
        return ' '.join([e for e in extra if e])

    def _collect_lambda_content(self, destination):

        if os.path.isfile(os.path.join(self.get_root(), self.settings['code'])):
            self._collect_lambda_file_content(destination)
        else:
            self._collect_lambda_module_content(destination)
            code_root = os.path.join(self.get_root(), self.settings['code'])
            requirements_path = os.path.join(code_root, 'requirements.txt')

            if os.path.isfile(requirements_path):
                setup_cfg_path = os.path.join(destination, 'setup.cfg')

                with open(setup_cfg_path, 'w') as f:
                    f.write("[install]\nprefix=")

                command = "{} install -r {} -q -t {} {}".format(
                    self._pip_path(),
                    requirements_path,
                    destination,
                    self._pip_extra()
                )

                subprocess.check_output(
                    command,
                    shell=True,
                    stderr=subprocess.STDOUT
                )

                os.remove(setup_cfg_path)

class NodeLambda(Lambda):

    runtime = 'nodejs'
    base_runtime = 'node'
    extension = 'js'

    def _npm_path(self):
        return self.project.settings.get('npm-path', 'npm')

    def _npm_extra(self):
        extra = (
            self.project.settings.get('npm-extra'),
            self.app and self.app.settings.get('npm-extra'),
            self.settings.get('npm-extra'),
        )
        return ' '.join([e for e in extra if e])

    def _collect_lambda_content(self, destination):
        """Collect node requirements using ``npm``"""

        if os.path.isfile(os.path.join(self.get_root(), self.settings['code'])):
            self._collect_lambda_file_content(destination)
        else:
            self._collect_lambda_module_content(destination)
            code_root = os.path.join(self.get_root(), self.settings['code'])
            package_json_path = os.path.join(destination, 'package.json')

            if os.path.isfile(package_json_path):
                command = "cd {} && {} install {}".format(
                    destination,
                    self._npm_path(),
                    self._npm_extra()
                )
                subprocess.check_output(
                    command,
                    shell=True,
                    stderr=subprocess.STDOUT
                )


class JavaLambda(Lambda):

    runtime = 'java8'
    base_runtime = 'java'
    extension = 'java'

    def _gradle_path(self):
        return self.project.settings.get('gradle-path', 'gradle')

    def _gradle_extra(self):
        extra = (
            self.project.settings.get('gradle-extra'),
            self.app and self.app.settings.get('gradle-extra'),
            self.settings.get('gradle-extra'),
        )
        return ' '.join([e for e in extra if e])

    def _collect_lambda_content(self, destination):
        root = os.path.join(self.get_root(), self.settings['code'])
        command = "cd {} && {} build -Pdest={} {}".format(
            root,
            self._gradle_path(),
            destination,
            self._gradle_extra()
        )
        output = subprocess.check_output(
            command,
            shell=True,
            stderr=subprocess.STDOUT
        )
