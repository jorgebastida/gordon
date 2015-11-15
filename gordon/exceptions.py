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
    hint = "Cloudformation status is {}, which is bad."
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
