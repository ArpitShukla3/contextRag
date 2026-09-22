"""Markdown document parser."""

from app.services.parsing.base import DocumentParser, ParsedDocument, ParsedPage


class MarkdownParser(DocumentParser):
    """Parser for Markdown files (raw text preserved verbatim)."""

    extensions = frozenset({".md", ".markdown"})
    content_types = frozenset({"text/markdown", "text/x-markdown"})

    def parse(self, content: bytes) -> ParsedDocument:
        text = content.decode("utf-8-sig", errors="replace")
        return ParsedDocument(
            pages=[ParsedPage(text=text)],
            metadata={"format": "markdown"},
        )