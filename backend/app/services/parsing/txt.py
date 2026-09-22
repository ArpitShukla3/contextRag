"""Plain text document parser."""

from app.services.parsing.base import DocumentParser, ParsedDocument, ParsedPage


class TxtParser(DocumentParser):
    """Parser for UTF-8 plain text files."""

    extensions = frozenset({".txt"})
    content_types = frozenset({"text/plain", "text/plain; charset=utf-8"})

    def parse(self, content: bytes) -> ParsedDocument:
        text = content.decode("utf-8-sig", errors="replace")
        return ParsedDocument(
            pages=[ParsedPage(text=text)],
            metadata={"format": "txt"},
        )