"""Uploaded file validation."""

from pathlib import PurePath

from app.exceptions import FileValidationError


class FileValidator:
    """Validate an incoming uploaded file before ingestion."""

    def __init__(self, allowed_suffixes: set[str], max_size_bytes: int) -> None:
        self._allowed = set(allowed_suffixes)
        self._max_size_bytes = max_size_bytes

    def validate(self, *, original_filename: str, content: bytes) -> None:
        suffix = PurePath(original_filename or "").suffix.lower()

        if suffix not in self._allowed:
            supported = ", ".join(sorted(self._allowed))
            label = suffix or "(no extension)"
            raise FileValidationError(
                f"Unsupported file type {label!r}. Supported types: {supported}."
            )

        if len(content) == 0:
            raise FileValidationError("Uploaded file is empty.")

        if len(content) > self._max_size_bytes:
            limit_mb = self._max_size_bytes // (1024 * 1024)
            raise FileValidationError(
                f"File exceeds the maximum allowed size of {limit_mb} MB."
            )