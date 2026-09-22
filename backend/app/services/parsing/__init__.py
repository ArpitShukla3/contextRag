"""Document parsing subsystem (extensible parser registry)."""

from app.services.parsing.base import (
    DocumentParser,
    ParsedDocument,
    ParsedPage,
)
from app.services.parsing.docx import DocxParser
from app.services.parsing.markdown import MarkdownParser
from app.services.parsing.pdf import PdfParser
from app.services.parsing.registry import ParserRegistry, create_parser_registry
from app.services.parsing.txt import TxtParser

__all__ = [
    "DocxParser",
    "DocumentParser",
    "MarkdownParser",
    "ParsedDocument",
    "ParsedPage",
    "ParserRegistry",
    "PdfParser",
    "TxtParser",
    "create_parser_registry",
]