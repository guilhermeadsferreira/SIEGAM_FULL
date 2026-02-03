class InfrastructureException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class RetryableException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class NonRetryableException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class NetworkException(RetryableException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class FileValidationException(NonRetryableException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ParseException(NonRetryableException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
