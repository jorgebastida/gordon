# -*- coding: utf-8 -*-
import os
import sys
import shutil
import tempfile
import zipfile
import subprocess
import platform

import six
import troposphere
from troposphere import iam, awslambda, s3
from clint.textui import colored, indent

from gordon import actions
from gordon import utils
from gordon import exceptions
from gordon.contrib.lambdas.resources import LambdaVersion
from . import base


class Lambda(base.BaseResource):
    """Base Lambda Resource which defines all shared resources between
    runtimes.
    """

    REQUIRED_SETTINGS = ('code', )
    code_filename = 'code'
    grn_type = 'lambda'
    _default_runtime = None
    _runtimes = {}

    @classmethod
    def factory(cls, *args, **kwargs):
        """Returns an instance of one of the severeal available Lambda
        resources based on the runtime."""
        _, extension = os.path.splitext(kwargs['settings']['code'])
        runtime = kwargs['settings'].get('runtime', '')

        if 'python' in runtime or extension == '.py':
            return PythonLambda(*args, **kwargs)
        elif 'node' in runtime or extension == '.js':
            return NodeLambda(*args, **kwargs)
        elif 'java' in runtime:
            return JavaLambda(*args, **kwargs)
        else:
            raise exceptions.InvalidLambdaCodeExtensionError(extension)

    def __init__(self, *args, **kwargs):
        super(Lambda, self).__init__(*args, **kwargs)
        self.current_alias_project_name = '{}:current'.format(self.in_project_name)
        self.current_alias_cf_name = utils.valid_cloudformation_name(self.name, "CurrentAlias")

        self.project.register_resource_reference(
            self.current_alias_project_name,
            self.current_alias_cf_name,
            self
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

    def get_runtime(self):
        """Returns the runtime for this lambda."""
        runtime = self.settings.get('runtime', self._default_runtime)
        return self._runtimes[runtime]

    def get_context_key(self):
        return self.settings.get('context', 'default')

    def get_context_destination(self):
        return self.settings.get('context-destinaton', '.context')

    def _get_policies(self):
        """Returns a list of policies to attach to the IAM Role of this Lambda.
        Users can add more policies to this Role by defining policy documents
        in the settings of the lambda under the ``policies`` key."""

        policies = []

        if self._get_true_false('auto-run-policy', 't'):
            policies.append(
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
                )
            )

        if self.settings.get('vpc') and self._get_true_false('auto-vpc-policy', 't'):
            policies.append(
                iam.Policy(
                    PolicyName=utils.valid_cloudformation_name(self.name, 'vpc'),
                    PolicyDocument={
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "ec2:CreateNetworkInterface"
                                ],
                                "Resource": [
                                    "*"
                                ]
                            }
                        ]
                    }
                )
            )

        for policy_nme, policy_document in six.iteritems(self.settings.get('policies', {})):
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
        is defined, gordon will create and assign one with the basic
        permissions suggested by AWS.

        Users can customize the policies attached to the role using
        ``policies`` in the lambda settings."""

        role = self.settings.get('role')

        if isinstance(role, six.string_types) or isinstance(role, troposphere.Ref):
            return role
        elif role is None:
            pass
        else:
            raise exceptions.InvalidLambdaRoleError(self.name, role)

        return iam.Role(
            utils.valid_cloudformation_name(self.name, 'role'),
            AssumeRolePolicyDocument={
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {
                        "Service": ["lambda.amazonaws.com"]
                    },
                    "Action": ["sts:AssumeRole"]
                }]
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

        bucket_name = troposphere.Join(
            "-",
            [
                utils.validate_code_bucket(project.settings['code-bucket']),
                troposphere.Ref(troposphere.AWS_REGION),
                troposphere.Ref('Stage')
            ]
        )
        code_bucket = s3.Bucket(
            "CodeBucket",
            BucketName=bucket_name,
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
                Value=bucket_name,
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

        extra = {}
        if self.settings.get('vpc'):
            vpc = self.project.get_resource('vpc::{}'.format(self.settings.get('vpc')))

            if isinstance(vpc.settings['security-groups'], troposphere.Ref):
                vpc.settings['security-groups']._type = 'List<AWS::EC2::SecurityGroup::Id>'

            if isinstance(vpc.settings['subnet-ids'], troposphere.Ref):
                vpc.settings['subnet-ids']._type = 'List<AWS::EC2::Subnet::Id>'

            extra['VpcConfig'] = awslambda.VPCConfig(
                SecurityGroupIds=vpc.settings['security-groups'],
                SubnetIds=vpc.settings['subnet-ids']
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
                Runtime=self.get_runtime(),
                Timeout=self.get_timeout(),
                **extra
            )
        )

        lambda_version = 'lambda:contrib_lambdas:version'
        lambda_ref = troposphere.GetAtt(self.project.reference(lambda_version), 'Arn')
        if not self.in_project_name.startswith('lambda:contrib_lambdas:'):
            lambda_version = '{}:current'.format(lambda_version)
            lambda_ref = troposphere.Ref(self.project.reference(lambda_version))

        version = template.add_resource(
            LambdaVersion.create_with(
                utils.valid_cloudformation_name(self.name, "Version"),
                DependsOn=[
                    self.project.reference(lambda_version),
                    function.name
                ],
                lambda_arn=lambda_ref,
                FunctionName=troposphere.Ref(
                    function
                ),
                S3ObjectVersion=troposphere.Ref(
                   utils.valid_cloudformation_name(self.name, "s3version")
                ),
            )
        )

        alias = template.add_resource(
            awslambda.Alias(
                self.current_alias_cf_name,
                DependsOn=[
                    version.name
                ],
                FunctionName=troposphere.Ref(
                    function
                ),
                FunctionVersion=troposphere.GetAtt(
                    version, "Version"
                ),
                Name="current",
            )
        )
        if self._get_true_false('cli-output', 't'):
            template.add_output([
                troposphere.Output(
                    utils.valid_cloudformation_name("Clioutput", self.in_project_name),
                    Value=troposphere.Ref(alias),
                )
            ])

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
        with open(filename, 'wb') as f:
            f.write(self.get_zip_file().read())

        context, context_key = {}, self.get_context_key()
        try:
            lambda_context = self.project.get_resource('contexts::{}'.format(context_key))
        except exceptions.ResourceNotFoundError:
            if context_key != 'default':
                raise
        else:
            context = lambda_context.settings

        template.add(
            actions.InjectContextAndUploadToS3(
                name="{}-upload".format(self.name),
                bucket=actions.Ref(name='CodeBucket'),
                key=self.get_bucket_key(),
                filename=os.path.relpath(filename, self.project.build_path),
                context_to_inject=context,
                context_destinaton=self.get_context_destination()
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

    def collect_and_run(self, stdin):
        self.project.create_workspace()
        destination = tempfile.mkdtemp(dir=self.project.get_workspace())

        # Translate pythona architecture to go architecture.
        # https://go.googlesource.com/go/+/master/src/cmd/dist/build.go#1086
        go_target_arch = {'i386': '386', 'x86_64': 'amd64'}[platform.processor()]

        try:
            self._collect_lambda_content(
                destination,
                go_target_os=platform.system().lower(),
                go_target_arch=go_target_arch
            )
        except subprocess.CalledProcessError as exc:
            shutil.rmtree(destination)
            raise exceptions.LambdaBuildProcessError(exc, self)

        try:
            self.run(destination, stdin)
        finally:
            shutil.rmtree(destination)

    def _get_default_run_command(self):
        raise NotImplementedError()

    def _get_loader_requirements(self):
        return []

    def run(self, path, stdin):
        for source, dest in self._get_loader_requirements():
            shutil.copyfile(
                os.path.join(self.project._gordon_root, 'loaders', source),
                os.path.join(path, dest)
            )

        command = self.settings.get('run', self._get_default_run_command())
        command = command.format(
            lambda_path=path,
            name=self.name,
            memory=self.get_memory(),
            handler=self.get_handler(),
            timeout=self.get_timeout()
        )

        with utils.cd(path):
            try:
                out = subprocess.check_output(
                    command,
                    shell=True,
                    stdin=stdin,
                    stderr=subprocess.STDOUT
                )
            except subprocess.CalledProcessError as exc:
                print(exc.output)
            else:
                print(out.decode('utf-8'))

    def get_zip_file(self):
        """Returns a zip file file-like object with all the required source
        on it."""

        self.project.create_workspace()
        destination = tempfile.mkdtemp(dir=self.project.get_workspace())

        try:
            self._collect_lambda_content(destination)
        except subprocess.CalledProcessError as exc:
            shutil.rmtree(destination)
            raise exceptions.LambdaBuildProcessError(exc, self)

        with tempfile.SpooledTemporaryFile(0, 'wb') as tmp:
            with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zf:
                for basedir, dirs, files in os.walk(destination):
                    relative = os.path.relpath(basedir, destination)
                    for filename in files:
                        source = os.path.join(destination, basedir, filename)
                        relative_destination = os.path.join(relative, filename)
                        if six.PY2:
                            source = source.decode('utf-8', errors='strict')
                            relative_destination = relative_destination.decode('utf-8', errors='strict')
                        zf.write(source, relative_destination)

            tmp.seek(0)
            output = six.BytesIO(tmp.read())

        output.seek(0)
        shutil.rmtree(destination)
        return output

    def _collect_lambda_file_content(self, destination):
        filename = '{}.{}'.format(self.code_filename, self.extension)
        shutil.copyfile(os.path.join(self.get_root(), self.settings['code']), os.path.join(destination, filename))

    def _get_build_command(self, destination):
        return self.settings.get('build', self._get_default_build_command(destination))

    def _collect_lambda_content(self, destination, **kwargs):
        """Collects all required files to be included in the .zip file of the
        lambda. Returns a temporal directory path
        """
        if os.path.isfile(os.path.join(self.get_root(), self.settings['code'])):
            self._collect_lambda_file_content(destination)
        else:
            self._collect_lambda_module_content(destination, **kwargs)

    def _collect_lambda_module_content(self, destination, go_target_arch='amd64', go_target_os='linux'):
        root = os.path.join(self.get_root(), self.settings['code'])
        with utils.cd(root):
            commands = self._get_build_command(destination)
            if hasattr(commands, '__call__'):
                commands()
                return
            elif isinstance(commands, six.string_types):
                commands = [commands]

            for command in commands:
                command = command.format(
                    target=destination,
                    pip_path=self._pip_path(),
                    npm_path=self._npm_path(),
                    gradle_path=self._gradle_path(),
                    pip_install_extra=self._pip_install_extra(),
                    npm_install_extra=self._npm_install_extra(),
                    gradle_build_extra=self._gradle_build_extra(),
                    project_path=self.project.path,
                    project_name=self.project.name,
                    lambda_name=self.name,
                    go_target_os=go_target_os,
                    go_target_arch=go_target_arch,
                )
                if self.project.debug:
                    with indent(4):
                        self.project.puts(colored.white(command))
                out = subprocess.check_output(
                    command,
                    shell=True,
                    stderr=subprocess.STDOUT
                )
                if self.project.debug and out:
                    with indent(4):
                        self.project.puts(out.decode("utf-8"))

    def _collect_folder(self, source, destination):
        for basedir, dirs, files in os.walk(source):
            relative = os.path.relpath(basedir, source)
            for filename in files:
                relative_destination = os.path.join(relative, filename)
                shutil.copyfile(os.path.join(basedir, filename), os.path.join(destination, relative_destination))

    def _get_default_build_command(self, destination):
        raise NotImplementedError

    def _gradle_path(self):
        return self.project.settings.get('gradle-path', 'gradle')

    def _gradle_build_extra(self):
        extra = (
            self.project.settings.get('gradle-build-extra'),
            self.app and self.app.settings.get('gradle-build-extra'),
            self.settings.get('gradle-build-extra'),
        )
        return ' '.join([e for e in extra if e])

    def _pip_path(self):
        return self.project.settings.get('pip-path', 'pip')

    def _pip_install_extra(self):
        extra = (
            self.project.settings.get('pip-install-extra'),
            self.app and self.app.settings.get('pip-install-extra'),
            self.settings.get('pip-install-extra'),
        )
        return ' '.join([e for e in extra if e])

    def _npm_path(self):
        return self.project.settings.get('npm-path', 'npm')

    def _npm_install_extra(self):
        extra = (
            self.project.settings.get('npm-install-extra'),
            self.app and self.app.settings.get('npm-install-extra'),
            self.settings.get('npm-install-extra'),
        )
        return ' '.join([e for e in extra if e])


class PythonLambda(Lambda):

    _default_runtime = 'python2.7'
    _runtimes = {
        'python': 'python2.7',
        'python2.7': 'python2.7',
        'python2': 'python2.7'
    }
    extension = 'py'

    def _get_default_build_command(self, destination):
        code_root = os.path.join(self.get_root(), self.settings['code'])
        requirements_path = os.path.join(code_root, 'requirements.txt')

        commands = []
        commands.append('cp -Rf * {target}')
        if os.path.isfile(requirements_path):
            commands.append('{pip_path} install --install-option="--prefix=" -r requirements.txt -q -t {target} {pip_install_extra}')
            commands.append('cd {target} && find . -name "*.pyc" -delete')
        return commands

    def _get_default_run_command(self):
        return 'touch __init__.py && python _gloader.py {handler} {name} {memory} {timeout}'

    def _get_loader_requirements(self):
        return [['python.py', '_gloader.py']]


class NodeLambda(Lambda):

    _default_runtime = 'nodejs4.3'
    _runtimes = {
        'node': 'nodejs',
        'nodejs': 'nodejs',
        'nodejs4.3': 'nodejs4.3',
        'nodejs0.10': 'nodejs',
        'node0.10': 'nodejs'
    }
    extension = 'js'

    def _get_default_build_command(self, destination):
        code_root = os.path.join(self.get_root(), self.settings['code'])
        package_json_path = os.path.join(code_root, 'package.json')

        commands = []
        commands.append('cp -Rf * {target}')
        if os.path.isfile(package_json_path):
            commands.append('cd {target} && {npm_path} install {npm_install_extra}')
        return commands

    def _get_default_run_command(self):
        return 'node _gloader.js {handler} {name} {memory} {timeout}'

    def _get_loader_requirements(self):
        return [['node.js', '_gloader.js']]


class JavaLambda(Lambda):

    _default_runtime = 'java8'
    _runtimes = {
        'java': 'java8',
        'java8': 'java8',
    }
    extension = 'java'

    def _get_loader_requirements(self):
            return [['java/build/libs/java.jar', '_gloader.jar']]

    def _get_default_build_command(self, destination):
        return "{gradle_path} build -Ptarget={target} {gradle_build_extra}"

    def _get_default_run_command(self):
        return 'java -cp "_gloader.jar:lib/*:." gordon.GordonLoader {handler} {name} {memory} {timeout}'
