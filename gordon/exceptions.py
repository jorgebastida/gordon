class BaseGordonException(Exception):
    pass

class ResourceSettingRequiredError(BaseGordonException):
    pass

class InvalidStreamStartingPositionError(BaseGordonException):
    pass

class InvalidLambdaRoleError(BaseGordonException):
    pass

class InvalidLambdaCodeExtensionError(BaseGordonException):
    pass

class ActionRequiredPropertyError(BaseGordonException):
    pass

class InvalidAppFormatError(BaseGordonException):
    pass

class DuplicateResourceNameError(BaseGordonException):
    pass

class ProjectNotBuildError(BaseGordonException):
    pass

class AbnormalCloudFormationStatusError(BaseGordonException):
    pass

class ProjectDirectoryAlreadyExistsError(BaseGordonException):
    pass

class AppDirectoryAlreadyExistsError(BaseGordonException):
    pass

class UnknownProtocolError(BaseGordonException):
    pass
    
class CloudFormationStackInProgressError(BaseGordonException):
    pass
