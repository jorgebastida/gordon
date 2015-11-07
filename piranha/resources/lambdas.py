import os
import zipfile
import StringIO

import troposphere
from troposphere import iam, awslambda, s3

from piranha import actions
from piranha import utils
from . import base

class Lambda(base.BaseResource):

    PYTHON_2_7_RUNTIME = 'python2.7'
    NODEJS_0_10_36_RUNTIME = 'nodejs'
    JAVA_8_RUNTIME = 'python2.7'

    EXTENSIONS = {
        PYTHON_2_7_RUNTIME: 'py',
        NODEJS_0_10_36_RUNTIME: 'js',
        JAVA_8_RUNTIME: 'java',
    }

    REQUIRED_SETTINGS = ('code', )

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

    def get_bucket_key(self):
        return "{}.zip".format(self.name)

    def get_zip_file(self):
        filename = 'code.{}'.format(self.EXTENSIONS.get(self.get_runtime()))
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
            BucketName=troposphere.Join('-', [troposphere.Ref("Stage"), project.name, 'piranha']),
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

    def register_resources_template(self, template):
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

    def register_pre_resources_template(self, template):
        code_path = os.path.join(self.app.project.build_path, 'code')
        if not os.path.exists(code_path):
            os.makedirs(code_path)

        template.add_parameter(
            name="CodeBucket",
        )

        filename = os.path.join(code_path, self.get_bucket_key())
        with open(filename, 'w') as f:
            f.write(self.get_zip_file().read())
            template.add(
                actions.UploadToS3(
                    bucket=actions.Ref('CodeBucket'),
                    key=self.get_bucket_key(),
                    filename=os.path.relpath(filename, self.app.project.build_path)
                )
            )
