"""Parser registry: maps file suffixes / MIME types to parsers."""

from pathlib import PurePath

from app.services.parsing.base import DocumentParser
from app.services.parsing.docx import DocxParser
from app.services.parsing.markdown import MarkdownParser
from app.services.parsing.pdf import PdfParser
from app.services.parsing.txt import TxtParser


class ParserRegistry:
    """Registry of parsers keyed by file suffix and MIME type."""

    def __init__(self) -> None:
        self._by_suffix: dict[str, DocumentParser] = {}
        self._by_content_type: dict[str, DocumentParser] = {}

    def register(self, parser: DocumentParser) -> None:
        """Register a parser under its supported suffixes and content types."""
        for extension in parser.extensions:
            self._by_suffix[extension] = parser
        for content_type in parser.content_types:
            self._by_content_type[content_type] = parser

    def get_for_suffix(self, filename: str) -> DocumentParser | None:
        """Return the parser suitable for a filename (case-insensitive)."""
        suffix = PurePath(filename or "").suffix.lower()
        return self._by_suffix.get(suffix)

    def get_for_content_type(self, content_type: str) -> DocumentParser | None:
        """Return the parser suitable for a MIME type (case-insensitive)."""
        return self._by_content_type.get((content_type or "").strip().lower())

    def suffixes(self) -> list[str]:
        """Return the sorted list of supported file suffixes."""
        return sorted(self._by_suffix)


def create_parser_registry() -> ParserRegistry:
    """Build the registry with the built-in parsers."""
    registry = ParserRegistry()
    registry.register(PdfParser())
    registry.register(TxtParser())
    registry.register(DocxParser())
    registry.register(MarkdownParser())
    return registry