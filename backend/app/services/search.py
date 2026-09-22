"""Search orchestration."""

from __future__ import annotations

from app.services.retrieval import RetrievedChunk, VectorRetriever


class SearchService:
    """Coordinates retrieval for the search endpoint."""

    def __init__(self, retriever: VectorRetriever) -> None:
        self._retriever = retriever

    def search(self, query: str, top_k: int = 10) -> list[RetrievedChunk]:
        return self._retriever.retrieve(query, top_k)