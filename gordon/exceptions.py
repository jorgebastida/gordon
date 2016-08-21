class BaseGordonException(Exception):

    code = 1
    hint = u"Something went't wrong"

    def get_hint(self):
        return self.hint.format(*self.args)


class ResourceSettingRequiredError(BaseGordonException):
    code = 2
    hint = u"Resource {} requires you to define '{}' in it's settings."


class InvalidStreamStartingPositionError(BaseGordonException):
    code = 3
    hint = u"Resource {} starting position '{}' is invalid."


class InvalidLambdaRoleError(BaseGordonException):
    hint = u"Resource {} role is invalid '{}'."
    code = 4


class InvalidLambdaCodeExtensionError(BaseGordonException):
    hint = u"{} extension is invalid."
    code = 5


class PropertyRequiredError(BaseGordonException):
    hint = u"Action {} requires you to define '{}' property."
    code = 6


class InvalidAppFormatError(BaseGordonException):
    hint = u"Invalid app format {}."
    code = 7


class DuplicateResourceNameError(BaseGordonException):
    hint = u"Duplicate resource error {} {}"
    code = 8


class ProjectNotBuildError(BaseGordonException):
    hint = u"It looks you have not build your project yet! Run $ gordon build"
    code = 9


class AbnormalCloudFormationStatusError(BaseGordonException):
    hint = u"""
    Oh Oh!! You stack status is {1}... which is bad, quite bad.
    The stack cannot return to a good state. In other words, a dependent
    resource cannot return to its original state, which causes a failure.

    What can you do now? Well... you need to delete the stack  and run this
    command again. Before doing that, it would be good if you check what
    failed... because it is quite possible this will happend again if you
    don't solve the root issue.

    You can either use the AWS Console, or use gordon's delete action.

    Keep in mind that deleting the stack will remove all resources deployed
    by Gordon (Lambdas, EventSourceMapping, APIGateways, etc...) which will
    generate disruption in your service (for obvious reasons).

    Because the nature of Gordon, all templates should be idempotent, so,
    if you apply your gordon project again after deleting your stack, the
    final result should be the same.

    It is going to be fine.

    Stack: {0}

    http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/troubleshooting.html#d0e114571
    """
    code = 10


class ProjectDirectoryAlreadyExistsError(BaseGordonException):
    hint = u"A directory with name '{}' already exists."
    code = 11


class AppDirectoryAlreadyExistsError(BaseGordonException):
    hint = u"A directory with name '{}' already exists."
    code = 12


class UnknownProtocolError(BaseGordonException):
    hint = u"Unknown protocol {} with value {}."
    code = 13


class CloudFormationStackInProgressError(BaseGordonException):
    hint = u"CloudFormation stack {} is in progress ({})."
    code = 14


class ResourceValidationError(BaseGordonException):
    code = 15

    def get_hint(self):
        return self.args[0]


class BaseProtocolError(BaseGordonException):

    def get_hint(self):
        return self.args[0]


class ProtocolNotFoundlError(BaseProtocolError):
    code = 16


class ProtocolMultipleMatcheslError(BaseProtocolError):
    code = 17


class DuplicateAppNameError(BaseGordonException):
    hint = u"An application with name {} is already installed."
    code = 18


class AppNotFoundError(BaseGordonException):
    hint = u"Application with name {} and path {} can't be found."
    code = 19


class ResourceNotFoundError(BaseGordonException):
    code = 20

    def get_hint(self):
        hint = u"Resource {} Not Found. Available {}".format(*self.args)

        try:
            resource = self.args[0].split(':')
            if resource[1].startswith('contrib_'):
                hint += (u"\n\nIt looks like {} is missing in your settings.yml "
                         u"file apps list").format(resource[1].replace('_', '.'))
        except IndexError:
            pass

        return hint


class LambdaBuildProcessError(BaseGordonException):

    code = 21

    def get_hint(self):
        return (
            u"Error building lambda '{}'!\n"
            u"cmd: {}\n\n"
            u"{}\n"
        ).format(
            self.args[1].name,
            self.args[0].cmd,
            self.args[0].output,
        )


class InvalidApigatewayIntegrationTypeError(BaseGordonException):
    hint = u"Invalid Apigateway integration type: {}"
    code = 22


class LambdaNotFound(BaseGordonException):
    hint = u"Lambda with name {} can't be found."
    code = 23


class ValidationError(BaseGordonException):
    hint = u"  Validation Error: {}"
    code = 24
