"""Tests for upload file validation."""

import pytest

from app.exceptions import FileValidationError
from app.services.validation import FileValidator

ALLOWED = {".pdf", ".txt", ".docx", ".md"}


@pytest.fixture()
def validator() -> FileValidator:
    return FileValidator(allowed_suffixes=ALLOWED, max_size_bytes=1024)


class TestAcceptedFiles:
    def test_accepts_supported_extension(self, validator):
        validator.validate(original_filename="report.txt", content=b"content")

    def test_extension_is_case_insensitive(self, validator):
        validator.validate(original_filename="REPORT.PDF", content=b"%PDF-x")


class TestInvalidFileTypes:
    def test_rejects_unknown_extension(self, validator):
        with pytest.raises(FileValidationError, match="Unsupported file type"):
            validator.validate(original_filename="malware.exe", content=b"x")

    def test_error_lists_supported_types(self, validator):
        with pytest.raises(FileValidationError, match=r"\.pdf.*\.txt") as excinfo:
            validator.validate(original_filename="notes.xls", content=b"x")
        assert "Supported types" in str(excinfo.value)

    def test_rejects_missing_extension(self, validator):
        with pytest.raises(FileValidationError, match="no extension"):
            validator.validate(original_filename="README", content=b"x")

    def test_rejects_missing_filename(self, validator):
        with pytest.raises(FileValidationError):
            validator.validate(original_filename="", content=b"x")


class TestEmptyDocuments:
    def test_rejects_empty_content(self, validator):
        with pytest.raises(FileValidationError, match="empty"):
            validator.validate(original_filename="doc.txt", content=b"")


class TestFileSize:
    def test_rejects_oversized_content(self, validator):
        huge = b"x" * (1024 + 1)
        with pytest.raises(FileValidationError, match="maximum allowed size"):
            validator.validate(original_filename="doc.txt", content=huge)

    def test_accepts_content_at_exact_limit(self, validator):
        validator.validate(original_filename="doc.txt", content=b"x" * 1024)