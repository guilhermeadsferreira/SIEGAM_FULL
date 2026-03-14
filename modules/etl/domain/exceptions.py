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


class CatalogEmptyException(NonRetryableException):
    """
    Lançada quando 'eventos' ou 'cidades' estão vazios no banco ETL.
    Indica que o seed não foi executado — não é um erro retryable.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
