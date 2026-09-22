"""Tests for the document parsers."""

import pytest

from app.exceptions import ParsingError
from app.services.parsing import (
    DocxParser,
    MarkdownParser,
    PdfParser,
    TxtParser,
    create_parser_registry,
)


class TestPdfParser:
    def test_extracts_text(self, pdf_bytes):
        parsed = PdfParser().parse(pdf_bytes)
        assert "Hello PDF" in parsed.text
        assert "Second PDF line" in parsed.text

    def test_page_numbers(self, multi_page_pdf_bytes):
        parsed = PdfParser().parse(multi_page_pdf_bytes)
        assert [page.page_number for page in parsed.pages] == [1, 2]
        assert parsed.pages[0].text == "Page one content"
        assert parsed.pages[1].text == "Page two content"

    def test_metadata_includes_format(self, pdf_bytes):
        parsed = PdfParser().parse(pdf_bytes)
        assert parsed.metadata["format"] == "pdf"
        assert parsed.metadata["page_count"] == 1

    def test_rejects_non_pdf_bytes(self):
        with pytest.raises(ParsingError, match="not a valid PDF"):
            PdfParser().parse(b"definitely not a pdf")

    def test_rejects_corrupt_bytes(self):
        with pytest.raises(ParsingError):
            PdfParser().parse(b"%PDF-1.7 this is truncated garbage")


class TestTxtParser:
    def test_preserves_content(self, txt_bytes):
        parsed = TxtParser().parse(txt_bytes)
        assert parsed.text == "Plain text content.\nSecond line."
        assert len(parsed.pages) == 1
        assert parsed.pages[0].page_number is None

    def test_handles_bom(self):
        parsed = TxtParser().parse(b"\xef\xbb\xbfbom content")
        assert parsed.text == "bom content"

    def test_empty_text_is_marked_empty(self):
        assert TxtParser().parse(b"   \n  ").is_empty


class TestDocxParser:
    def test_extracts_paragraphs(self, docx_bytes):
        parsed = DocxParser().parse(docx_bytes)
        assert parsed.text == "Hello DOCX\nSecond paragraph"

    def test_rejects_non_docx_bytes(self):
        with pytest.raises(ParsingError, match="Could not open DOCX"):
            DocxParser().parse(b"random bytes")


class TestMarkdownParser:
    def test_preserves_markdown(self, markdown_bytes):
        parsed = MarkdownParser().parse(markdown_bytes)
        assert parsed.text == "# Heading\n\nSome **bold** markdown text."
        assert parsed.metadata["format"] == "markdown"


class TestParserRegistry:
    def test_registers_all_suffixes(self):
        suffixes = set(create_parser_registry().suffixes())
        assert suffixes == {".pdf", ".txt", ".docx", ".md", ".markdown"}

    def test_lookup_by_suffix_is_case_insensitive(self):
        registry = create_parser_registry()
        assert isinstance(registry.get_for_suffix("REPORT.PDF"), PdfParser)
        assert isinstance(registry.get_for_suffix("notes.txt"), TxtParser)

    def test_lookup_unknown_suffix_returns_none(self):
        assert create_parser_registry().get_for_suffix("file.exe") is None

    def test_resolves_content_type(self):
        registry = create_parser_registry()
        assert isinstance(
            registry.get_for_content_type("application/pdf"), PdfParser
        )