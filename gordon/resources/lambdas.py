import os
import hashlib
import zipfile
import StringIO

import troposphere
from troposphere import iam, awslambda, s3

from gordon import actions
from gordon import utils
from . import base

class Lambda(base.BaseResource):

    PYTHON_2_7_RUNTIME = 'python2.7'
    NODEJS_0_10_36_RUNTIME = 'nodejs'
    JAVA_8_RUNTIME = 'java8'

    EXTENSIONS = {
        PYTHON_2_7_RUNTIME: 'py',
        NODEJS_0_10_36_RUNTIME: 'js',
        JAVA_8_RUNTIME: 'java',
    }

    REQUIRED_SETTINGS = ('code', )

    CODE_FILENAME = 'code'

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
        with open(os.path.join(self.app.path, self.settings['code']), 'r') as f:
            return f.read()

    def get_code_hash(self):
        return hashlib.sha1(self.get_code()).hexdigest()[:8]

    def get_handler(self):
        return self.settings.get('handler', '{}.handler'.format(self.CODE_FILENAME))

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
                         "Service": [ "lambda.amazonaws.com" ]
                      },
                      "Action": [ "sts:AssumeRole" ]
                   } ]
                },
                Policies=policies
            )


    def get_timeout(self):
        timeout = self.settings.get('timeout', 3)
        return max(min(timeout, 300), 1)

    def get_bucket_key(self):
        return "{}_{}.zip".format(self.name, self.get_code_hash())

    def get_zip_file(self):
        filename = '{}.{}'.format(self.CODE_FILENAME, self.EXTENSIONS.get(self.get_runtime()))
        output = StringIO.StringIO()
        zipzile = zipfile.ZipFile(output, 'w')
        zipzile.write(os.path.join(self.app.path, self.settings['code']), filename)
        zipzile.close()
        output.seek(0)
        return output

    @classmethod
    def register_type_project_template(cls, project, template):
        code_bucket = s3.Bucket(
            "CodeBucket",
            BucketName=troposphere.Join('-', ['gordon', troposphere.Ref("Region"), troposphere.Ref("Stage"), project.name]),
            AccessControl=s3.Private,
        )
        template.add_resource(code_bucket)
        template.add_output([
            troposphere.Output(
                "CodeBucket",
                Description="CodeBucket name",
                Value=troposphere.Ref(code_bucket),
            )
        ])

    @classmethod
    def register_type_resources_template(cls, project, template):
        template.add_parameter(
            troposphere.Parameter(
                "CodeBucket",
                Description="Bucket where the code is located.",
                Type="String",
            )
        )

    def register_resources_template(self, template):
        role = self.get_role()
        depends_on = []
        if isinstance(role, iam.Role):
            template.add_resource(role)
            depends_on.append(role.name)
            role = troposphere.GetAtt(role, 'Arn')

        template.add_resource(
            awslambda.Function(
                self.name,
                DependsOn=depends_on,
                Code=awslambda.Code(
                    S3Bucket=troposphere.Ref("CodeBucket"),
                    S3Key=self.get_bucket_key(),
                ),
                Description=self.settings.get('description', ''),
                Handler=self.get_handler(),
                MemorySize=self.get_memory(),
                Role=role,
                Runtime=self.get_runtime(),
                Timeout=self.get_timeout()
            )
        )

    def register_pre_resources_template(self, template):
        code_path = os.path.join(self.app.project.build_path, 'code')
        if not os.path.exists(code_path):
            os.makedirs(code_path)

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
                    filename=os.path.relpath(filename, self.app.project.build_path)
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
