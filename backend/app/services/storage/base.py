"""Storage abstraction."""

from __future__ import annotations

import abc


class Storage(abc.ABC):
    """Contract for persisting and retrieving uploaded files."""

    @abc.abstractmethod
    def save(self, name: str, content: bytes) -> None:
        """Persist ``content`` under ``name``."""

    @abc.abstractmethod
    def read(self, name: str) -> bytes:
        """Return the content stored under ``name``."""

    @abc.abstractmethod
    def delete(self, name: str) -> None:
        """Remove the content stored under ``name`` (idempotent)."""

    @abc.abstractmethod
    def exists(self, name: str) -> bool:
        """Return whether content exists under ``name``."""