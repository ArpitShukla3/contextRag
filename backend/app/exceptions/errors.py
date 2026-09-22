"""Application exceptions."""


class AppError(Exception):
    """Base class for all application-level errors."""

    status_code: int = 500

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    status_code = 404


class ConflictError(AppError):
    """Raised when a request conflicts with the current state."""

    status_code = 409


class ProcessingError(AppError):
    """Raised when an internal processing step fails."""

    status_code = 500


class FileValidationError(AppError):
    """Raised when an uploaded file fails validation."""

    status_code = 422


class ParsingError(AppError):
    """Raised when document content cannot be parsed."""

    status_code = 422


class LLMError(AppError):
    """Raised when an LLM provider call fails."""

    status_code = 502