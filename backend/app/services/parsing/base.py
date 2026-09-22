"""Document parser abstraction."""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ParsedPage:
    """A single page of parsed document text."""

    text: str
    page_number: int | None = None


@dataclass(frozen=True)
class ParsedDocument:
    """Normalized output of a document parser."""

    pages: list[ParsedPage] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def text(self) -> str:
        """All page text joined together."""
        return "\n\n".join(page.text for page in self.pages)

    @property
    def is_empty(self) -> bool:
        """True when no page contributes meaningful text."""
        return not any(page.text.strip() for page in self.pages)


class DocumentParser(abc.ABC):
    """Abstract contract for turning raw file bytes into normalized text."""

    extensions: frozenset[str] = frozenset()
    content_types: frozenset[str] = frozenset()

    @abc.abstractmethod
    def parse(self, content: bytes) -> ParsedDocument:
        """Parse raw file content into a :class:`ParsedDocument`."""