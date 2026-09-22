"""PDF document parser (PyMuPDF)."""

from app.exceptions import ParsingError
from app.services.parsing.base import DocumentParser, ParsedDocument, ParsedPage

try:
    import pymupdf
except ImportError as exc:  # pragma: no cover - dependency missing
    raise ImportError("PyMuPDF is required for PDF parsing.") from exc


class PdfParser(DocumentParser):
    """Parser for PDF files using PyMuPDF."""

    extensions = frozenset({".pdf"})
    content_types = frozenset({"application/pdf"})

    def parse(self, content: bytes) -> ParsedDocument:
        if not content.lstrip()[:1024].startswith(b"%PDF-"):
            raise ParsingError("File is not a valid PDF.")

        try:
            document = pymupdf.open(stream=content, filetype="pdf")
        except Exception as exc:
            raise ParsingError("Could not open PDF: the file is corrupt.") from exc

        pages: list[ParsedPage] = []
        try:
            for index in range(len(document)):
                page = document.load_page(index)
                pages.append(
                    ParsedPage(
                        text=page.get_text().strip(),
                        page_number=index + 1,
                    )
                )
        finally:
            document.close()

        if not pages:
            raise ParsingError("PDF contains no pages.")

        return ParsedDocument(
            pages=pages,
            metadata={"format": "pdf", "page_count": len(pages)},
        )