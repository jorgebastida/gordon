class BasePiranhaException(Exception):
    pass

class UnknownAppFormat(BasePiranhaException):
    pass

class AbnormalCloudFormationStatusError(BasePiranhaException):
    pass

class CloudFormationStackInProgressError(BasePiranhaException):
    pass
