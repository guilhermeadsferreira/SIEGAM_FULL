"""Hierarquia de exceções para retry e tratamento de erros."""


class InfrastructureException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class RetryableException(Exception):
    """Erros de rede, SMTP, Z-API - podem ser retentados."""
    def __init__(self, message: str) -> None:
        super().__init__(message)


class NonRetryableException(Exception):
    """Erros de template, validação - não devem ser retentados."""
    def __init__(self, message: str) -> None:
        super().__init__(message)


class SmtpException(RetryableException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class WhatsAppApiException(RetryableException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class DatabaseException(InfrastructureException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
