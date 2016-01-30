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
        _, extension = os.path.splitext(kwargs['settings'].get('code'))

        if extension == '.py':
            return PythonLambda(*args, **kwargs)
        elif extension == '.js':
            return NodeLambda(*args, **kwargs)
        else:
            # TODO: Fix this self.name
            raise exceptions.InvalidLambdaCodeExtensionError(self.name, extension)

    def __init__(self, *args, **kwargs):
        super(Lambda, self).__init__(*args, **kwargs)

        self.current_alias_project_name = '{}:current'.format(self.in_project_name)
        self.current_alias_cf_name = utils.valid_cloudformation_name(self.name, "CurrentAlias")

        self.project.register_resource_reference(
            self.current_alias_project_name,
            self.current_alias_cf_name
        )

    def get_code(self):
        """Returns the sourcecode of the lambda."""
        with open(os.path.join(self.get_root(), self.settings['code']), 'r') as f:
            return f.read()

    def get_hash(self):
        """Returns an consistent hash of the sourcecode of the lambda."""
        return hashlib.sha1(self.get_code()).hexdigest()[:8]

    def get_handler(self):
        """Returns the name of the handler. If there is no any available in
        the settngs we assume is ``handler``."""
        return self.settings.get('handler', '{}.handler'.format(self.code_filename))

    def get_requirements(self):
        """Returns the requirements for this lambda based on the requirements
        of the project, app and lambda."""
        settings_name = '{}_requirements'.format(self.base_runtime)
        sources = (
            self.app.project.settings.get(settings_name, []),
            self.app.settings.get(settings_name, []),
            self.settings.get(settings_name, []),
        )

        for source in sources:
            for requirement in source:
                yield requirement

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

    def _collect_requirements(self, destination):
        """Collect runtime specific requirements."""
        pass

    def _collect_zip_content(self):
        """Collects all required files to be included in the .zip file of the
        lambda.

        This includes:
         - runtime requirements
         - project modules
         - app modules

        Returns a temporal directory path
        """
        destination = tempfile.mkdtemp()
        digest = hashlib.sha1()

        # Collect runtime requirements
        self._collect_requirements(destination)

        # Add requirements to the digest. We don't digest the content of the
        # required modules, but the name and version number (if included).
        # We need to reiterate in the the documentation how importat is to
        # freeze version numbers. In the future we could try to make the
        # particular implementations of __collect_requirements yield the
        # actual version numbers dowloaded, so we can make this more robust.
        for requirement in self.get_requirements():
            digest.update(requirement)

        # Collect app modules
        modules_paths = (
            os.path.join(self.get_root(), 'modules'),
            os.path.join(self.get_parent_root(), 'modules')

        )
        for path in modules_paths:

            # Modules might or might not exist.
            if not path or not os.path.exists(path):
                continue

            for base, dirs, files in os.walk(path):
                relative = os.path.relpath(base, path)
                for d in dirs:
                    relative_destination = os.path.join(destination, relative, d)
                    shutil.copytree(os.path.join(base, d), relative_destination)
                    digest.update(utils.tree_hash(relative_destination))

                for filename in files:
                    relative_destination = os.path.join(destination, relative, filename)
                    shutil.copyfile(os.path.join(base, filename), relative_destination)
                    digest.update(utils.file_hash(relative_destination))

        # Copy lambda code
        filename = '{}.{}'.format(self.code_filename, self.extension)
        shutil.copyfile(os.path.join(self.get_root(), self.settings['code']), os.path.join(destination, filename))
        digest.update(utils.file_hash(os.path.join(destination, filename)))

        # Calculate digest of destination
        with open(os.path.join(destination, '.metadata'), 'w') as f:
            f.write(json.dumps({'sha1': digest.hexdigest()}))

        return destination

    def get_zip_file(self):
        """Returns a zip file file-like object with all the required source
        on it."""
        tmp_directory = self._collect_zip_content()
        filename = '{}.{}'.format(self.code_filename, self.extension)
        output = StringIO.StringIO()
        zipzile = zipfile.ZipFile(output, 'w')

        for base, dirs, files in os.walk(tmp_directory):
            relative = os.path.relpath(base, tmp_directory)

            for filename in files:
                zipzile.write(os.path.join(tmp_directory, base, filename), os.path.join(relative, filename))

        zipzile.close()
        output.seek(0)
        shutil.rmtree(tmp_directory)
        return output

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


class PythonLambda(Lambda):

    runtime = 'python2.7'
    base_runtime = 'python'
    extension = 'py'

    def _collect_requirements(self, destination):
        """Collect python requirements using ``pip``"""
        setup_cfg_path = os.path.join(destination, 'setup.cfg')

        with open(setup_cfg_path, 'w') as f:
            f.write("[install]\nprefix=")

        for requirement in self.get_requirements():
            subprocess.check_output("pip install -q {} -t {}".format(requirement, destination), shell=True, stderr=subprocess.STDOUT)

        for name in os.listdir(destination):
            dist_dir = os.path.join(destination, name)
            if os.path.isdir(dist_dir) and name.endswith('.dist-info'):
                shutil.rmtree(dist_dir)

        os.remove(setup_cfg_path)


class NodeLambda(Lambda):

    runtime = 'nodejs'
    base_runtime = 'node'
    extension = 'js'

    def _collect_requirements(self, destination):
        """Collect node requirements using ``npm``"""

        for requirement in self.get_requirements():
            subprocess.check_output("cd {} && npm install {}".format(destination, requirement), shell=True, stderr=subprocess.STDOUT)
