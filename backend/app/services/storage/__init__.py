"""File storage subsystem (pluggable backend)."""

from app.services.storage.base import Storage
from app.services.storage.local import LocalDiskStorage

__all__ = ["LocalDiskStorage", "Storage"]