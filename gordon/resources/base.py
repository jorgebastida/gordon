import os

import troposphere
from troposphere import iam, awslambda, s3

from gordon import utils
from gordon.contrib.utils.cloudformation import Sleep

class BaseResource(object):

    required_settings = ()

    def __init__(self, name, settings, project=None, app=None):
        self.name = name
        self.app = app
        self.project = project or self.app.project
        self.settings = settings
        for key in self.required_settings:
            if key not in self.settings:
                raise Exception("Required setting {}".format(key))

        if self.app:
            self.in_project_name = '.'.join((self.app.name, self.name))
        else:
            self.in_project_name = self.name

        self.in_project_cf_name = utils.valid_cloudformation_name(self.in_project_name)

        self.project.register_resource_reference(
            self.in_project_name,
            self.in_project_cf_name
        )

    @classmethod
    def factory(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    @classmethod
    def register_type_pre_project_template(cls, project, template):
        pass

    @classmethod
    def register_type_project_template(cls, project, template):
        pass

    @classmethod
    def register_type_pre_resources_template(cls, project, template):
        pass

    @classmethod
    def register_type_resources_template(cls, project, template):
        pass

    @classmethod
    def register_type_post_resources_template(cls, project, template):
        pass

    def get_root(self):
        return self.app.path if self.app else self.project.path

    def register_pre_project_template(self, template):
        pass

    def register_project_template(self, template):
        pass

    def register_pre_resources_template(self, template):
        pass

    def register_resources_template(self, template):
        pass

    def register_post_resources_template(self, template):
        pass


class BaseStream(BaseResource):

    required_settings = (
        'stream',
        'starting_position',
        'lambda'
    )

    VALID_STARTING_POSITIONS = ('TRIM_HORIZON', 'LATEST')

    def get_batch_size(self):
        return max(min(self.settings.get('batch_size', 100), 10000), 1)

    def get_enabled(self):
        return str(self.settings.get('enabled', 't')).lower()[0] == 't'

    def get_starting_position(self):
        position = self.settings.get('starting_position')
        if position in self.VALID_STARTING_POSITIONS:
            return position
        raise Exception("Invalid starting_position {}".format(position))

    def get_function_name(self):
        return self.project.reference(
            self.settings.get('lambda')
        )

    def register_resources_template(self, template):

        sleep = Sleep.create_with(
            utils.valid_cloudformation_name(self.name, "Sleep"),
            Time=30
        )
        template.add_resource(sleep)

        template.add_resource(
            awslambda.EventSourceMapping(
                utils.valid_cloudformation_name(self.name),
                DependsOn=[sleep.name, self.get_function_name()],
                BatchSize=self.get_batch_size(),
                Enabled=self.get_enabled(),
                EventSourceArn=self.settings.get('stream'),
                FunctionName=troposphere.Ref(self.get_function_name()),
                StartingPosition=self.get_starting_position()
            )
        )
