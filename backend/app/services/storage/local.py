"""Local disk storage backend."""

from pathlib import Path

from app.services.storage.base import Storage


class LocalDiskStorage(Storage):
    """Store files on the local filesystem under a base directory."""

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        if Path(name).name != name:
            raise ValueError(f"Invalid storage key: {name!r}")
        return self.base_dir / name

    def save(self, name: str, content: bytes) -> None:
        self._path(name).write_bytes(content)

    def read(self, name: str) -> bytes:
        return self._path(name).read_bytes()

    def delete(self, name: str) -> None:
        self._path(name).unlink(missing_ok=True)

    def exists(self, name: str) -> bool:
        return self._path(name).is_file()