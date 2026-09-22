"""Vector (pgvector) retrieval."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Chunk, Document
from app.services.embeddings import EmbeddingProvider


@dataclass(frozen=True)
class RetrievedChunk:
    """A chunk returned by a retriever together with its document and score."""

    chunk: Chunk
    document: Document
    similarity: float

    @property
    def metadata(self) -> dict:
        return self.chunk.metadata_


class VectorRetriever:
    """Semantic search over chunk embeddings using pgvector cosine distance."""

    def __init__(self, session: Session, embedding_provider: EmbeddingProvider) -> None:
        self._session = session
        self._embeddings = embedding_provider

    def retrieve(self, query: str, top_k: int) -> list[RetrievedChunk]:
        """Return the top ``top_k`` chunks closest to ``query`` in embedding space."""
        if top_k <= 0:
            return []

        query_vector = self._embeddings.embed_one(query)
        distance = Chunk.embedding.cosine_distance(query_vector)
        statement = (
            select(Chunk, Document, (1 - distance).label("similarity"))
            .join(Document, Document.id == Chunk.document_id)
            .where(Chunk.embedding.is_not(None))
            .order_by(distance)
            .limit(top_k)
        )

        rows = self._session.execute(statement).all()
        return [
            RetrievedChunk(
                chunk=row.Chunk,
                document=row.Document,
                similarity=float(row.similarity),
            )
            for row in rows
        ]