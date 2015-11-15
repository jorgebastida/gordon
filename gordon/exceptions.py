class BaseGordonException(Exception):

    code = 1
    hint = "Something went't wrong"

    def get_hint(self):
        return self.hint.format(*self.args)


class ResourceSettingRequiredError(BaseGordonException):
    code = 2
    hint = "Resource {} requires you to define '{}' in it's settings."


class InvalidStreamStartingPositionError(BaseGordonException):
    code = 3
    hint = "Resource {} starting position '{}' is invalid."


class InvalidLambdaRoleError(BaseGordonException):
    hint = "Resource {} role is invalid '{}'."
    code = 4


class InvalidLambdaCodeExtensionError(BaseGordonException):
    hint = "Resource {} extension is invalid '{}'."
    code = 5


class PropertyRequiredError(BaseGordonException):
    hint = "Action {} requires you to define '{}' property."
    code = 6


class InvalidAppFormatError(BaseGordonException):
    hint = "Invalid app format {}."
    code = 7


class DuplicateResourceNameError(BaseGordonException):
    hint = "Duplicate resource error {} {}"
    code = 8


class ProjectNotBuildError(BaseGordonException):
    hint = "It looks you have not build your project yet! Run $ gordon build"
    code = 9


class AbnormalCloudFormationStatusError(BaseGordonException):
    hint = """
    Oh Oh!! You stack status is {1}... which is bad, quite bad.
    The stack cannot return to a good state. In other words, a dependent
    resource cannot return to its original state, which causes a failure.

    What can you do now? Well... you need to manually delete the stack from the
    CloudFormation console, and run this commanda again. Before doing that,
    it would be good if you check what failed... because it is quite possible
    this will happend again if you don't solve the root issue.

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
    hint = "A directory with name '{}' already exists."
    code = 11


class AppDirectoryAlreadyExistsError(BaseGordonException):
    hint = "A directory with name '{}' already exists."
    code = 12


class UnknownProtocolError(BaseGordonException):
    hint = "Unknown protocol {} with value {}."
    code = 13


class CloudFormationStackInProgressError(BaseGordonException):
    hint = "CloudFormation stack {} is in progress ({})."
    code = 14
