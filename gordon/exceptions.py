class BaseGordonException(Exception):
    pass

class UnknownAppFormat(BaseGordonException):
    pass

class AbnormalCloudFormationStatusError(BaseGordonException):
    pass

class CloudFormationStackInProgressError(BaseGordonException):
    pass
