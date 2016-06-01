import re

import troposphere
from troposphere import awslambda

from gordon import utils
from gordon.contrib.helpers.resources import Sleep
from gordon import exceptions


class BaseResource(object):
    """Resources are the core of gordon. A resource defines an entity which
    will require one or more CloudFormation/Custom resources to get created
    and wired together.

    This scaffold will allow resources to attach themsevels to the different
    hooks available trough the template building process.

    There are two different types of hooks:
     - Resource Type hooks
     - Resource Instance hooks

    Resource type hooks are helpful when you need to register resources only
    once regardless of the number of deployed instances. For example if we
    want to deploy a Lambda, we need a S3 bucket to upload the code, but we
    don't need one bucket per lambda.

    In the other hand, Resource instance hooks are evaluated once per instance.
    Following the same example, if we need three lambdas, we need to register
    three different lambda resources.

    Any Gordon project will define up to five stages where resources could be
    registered. Each of these stages allow resources to be registered both as
    type and instace resources.

    Available stages:
    - pre_project (custom)
    - project (troposphere)
    - pre_resources (custom)
    - resources (troposphere)
    - post_resources (custom)

    Because the nature of the resource settings is pretty dynamic, but there
    are  situations were some of them are mandatory, Resources can specify a
    list of ``required_settings`` so gordon will avoid proceeding if any of
    them is not defined.
    """
    grn_type = ''
    required_settings = ()

    def __init__(self, name, settings, project=None, app=None):
        self.name = name
        self.app = app
        self.project = project or self.app.project
        self.settings = settings
        for key in self.required_settings:
            if key not in self.settings:
                raise exceptions.ResourceSettingRequiredError(self.name, key)

        self.in_project_name = self._get_in_project_name()
        self.in_project_cf_name = utils.valid_cloudformation_name(
            self.in_project_name.split(':', 1)[1]
        )

        self.project.register_resource_reference(
            self.in_project_name,
            self.in_project_cf_name,
            self
        )

    def _get_in_project_name(self):
        """
        resource-type:my-app:my-resource
        resource-type::my-resource
        resource-type:my-app:my-resource
        """
        resource_path = [
            self.grn_type,
            self._get_grn_app(),
        ]
        return ':'.join(resource_path + list(self._get_grn_path()))

    def _get_grn_app(self):
        return self.app.name if self.app else ''

    def _get_grn_path(self):
        return [self._clean_grn_element(n) for n in self.get_grn_path()]

    def _clean_grn_element(self, value):
        return re.sub(r'[^\w\-\_\/]', '-', value)

    def get_grn_path(self):
        return [self.name]

    @classmethod
    def factory(cls, *args, **kwargs):
        """Most of the Resources are simple enough to not need this to be used,
        but there are certain situation where it is interesting to add another
        layer of inheritance instead of make resources be full of references
        to their kind. One example of this are Lambdas written in different
        languages. All of them share lot's of thing, but specific
        implementations for each runtime are different enough to have different
        types.
        """
        return cls(*args, **kwargs)

    @classmethod
    def register_type_pre_project_template(cls, project, template):
        """Hook to register custom resources before the project cloudformation
        stack is created.
        Note: This hook will be only executed once per resource type."""
        pass

    @classmethod
    def register_type_project_template(cls, project, template):
        """Hook to register troposphere resources in the project stack.
        Note: This hook will be only executed once per resource type."""
        pass

    @classmethod
    def register_type_pre_resources_template(cls, project, template):
        """Hook to register custom resources in the pre_resources template.
        This stack is applied between the project and resources stack.
        Note: This hook will be only executed once per resource type."""
        pass

    @classmethod
    def register_type_resources_template(cls, project, template):
        """Hook to register troposphere resources in the resources stack.
        This stack is applied between the pre_resources and the post_resources
        stack.
        Note: This hook will be only executed once per resource type."""
        pass

    @classmethod
    def register_type_post_resources_template(cls, project, template):
        """Hook to register custom resources in the post_resources template.
        This template is applied after the resources stack.
        Note: This hook will be only executed once per resource type."""
        pass

    def register_pre_project_template(self, template):
        """Hook to register custom resources before the project cloudformation
        stack is created."""
        pass

    def register_project_template(self, template):
        """Hook to register troposphere resources in the project stack."""
        pass

    def register_pre_resources_template(self, template):
        """Hook to register custom resources in the pre_resources template.
        This stack is applied between the project and resources stack."""
        pass

    def register_resources_template(self, template):
        """Hook to register troposphere resources in the resources stack.
        This stack is applied between the pre_resources and the post_resources
        stack."""
        pass

    def register_post_resources_template(self, template):
        """Hook to register custom resources in the post_resources template.
        This template is applied after the resources stack."""
        pass

    def get_root(self):
        """Returns the base path were this resource was defined"""
        return self.app.path if self.app else self.project.path

    def get_parent_root(self):
        """Returns the base path of the parent resource were this resource was
        defined"""
        return self.project.path if self.app else None

    def _get_true_false(self, field, default='t', settings=None):
        """Returns if this stream is enable or not."""
        return str((settings or self.settings).get(field, default)).lower()[0] == 't'

    def validate(self):
        """Check if the current resource can co-exist with the rest of the
        resources in the project. This is not suppose to be a thoughtful
        validation, but a safe net to make people experience better.
        If any validation error is found, this method must raise a
        ResourceValidationError exception otherwise, do nothing"""
        pass


class BaseStream(BaseResource):
    """BaseStream resource for all stream-based CloudFormation resources."""

    required_settings = (
        'stream',
        'starting_position',
        'lambda'
    )

    VALID_STARTING_POSITIONS = ('TRIM_HORIZON', 'LATEST')

    def get_batch_size(self):
        """Returns the size of the batch this source mapping is going to use.
        Current AWS limits are [100, 10000]."""
        return max(min(self.settings.get('batch_size', 100), 10000), 1)

    def get_enabled(self):
        """Returns if this stream is enable or not."""
        return self._get_true_false('enabled')

    def get_starting_position(self):
        """Returns the starting position for this stream. Valid options are
        available in ``VALID_STARTING_POSITIONS``."""
        position = self.settings.get('starting_position')
        if position in self.VALID_STARTING_POSITIONS:
            return position
        raise exceptions.InvalidStreamStartingPositionError(self.name, position)

    def get_function_name(self):
        """Returns a reference to the current alias of the lambda which will
        process this stream."""
        return self.project.reference(
            utils.lambda_friendly_name_to_grn(self.settings.get('lambda'))
        )

    def register_resources_template(self, template):
        """Register one ``EventSourceMapping`` into the resources template.

        Note: We preprend a 30s Sleep before the creation of this resource
        because the IAM role of the lambda is not propagated fast enough uppon
        creation, and CloudFormation checks if the referenced lambda has
        permission to consume this stream on creation time.

        Because the ``Lambda`` and the ``EventSourceMapping`` are created in
        the same stack we need to introduce this as palliative measure, sorry!
        """
        sleep_lambda = 'lambda:contrib_helpers:sleep:current'
        sleep = Sleep.create_with(
            utils.valid_cloudformation_name(self.name, "Sleep"),
            DependsOn=[self.project.reference(sleep_lambda)],
            lambda_arn=troposphere.Ref(self.project.reference(sleep_lambda)),
            Time=30
        )
        template.add_resource(sleep)

        template.add_resource(
            awslambda.EventSourceMapping(
                self.in_project_cf_name,
                DependsOn=[sleep.name, self.get_function_name()],
                BatchSize=self.get_batch_size(),
                Enabled=self.get_enabled(),
                EventSourceArn=self.settings.get('stream'),
                FunctionName=troposphere.Ref(self.get_function_name()),
                StartingPosition=self.get_starting_position()
            )
        )
