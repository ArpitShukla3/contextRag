"""Chunk data access."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Chunk


@dataclass(frozen=True)
class ChunkDraft:
    """Ready-to-persist chunk data."""

    chunk_index: int
    original_content: str
    metadata: dict[str, Any] = field(default_factory=dict)


class ChunkRepository:
    """Data-access operations for the ``chunks`` table."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def bulk_insert(self, document_id: int, drafts: Sequence[ChunkDraft]) -> list[Chunk]:
        rows = [
            Chunk(
                document_id=document_id,
                chunk_index=draft.chunk_index,
                original_content=draft.original_content,
                metadata_=draft.metadata,
            )
            for draft in drafts
        ]
        self._session.add_all(rows)
        self._session.flush()
        return rows

    def list_by_document(self, document_id: int) -> list[Chunk]:
        statement = (
            select(Chunk)
            .where(Chunk.document_id == document_id)
            .order_by(Chunk.chunk_index)
        )
        return list(self._session.scalars(statement).all())

    def count_by_document(self, document_id: int) -> int:
        statement = select(Chunk.id).where(Chunk.document_id == document_id)
        return len(self._session.scalars(statement).all())