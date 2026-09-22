"""Search schemas."""

from pydantic import BaseModel, ConfigDict, Field

from app.services.retrieval import RetrievedChunk


class SearchRequest(BaseModel):
    """Payload for a vector search request."""

    query: str = Field(min_length=1, description="Natural-language query.")
    top_k: int = Field(default=10, ge=1, le=50)


class SearchResult(BaseModel):
    """A single retrieved chunk."""

    model_config = ConfigDict(from_attributes=True)

    chunk_id: int
    document_id: int
    filename: str
    original_filename: str
    content: str
    similarity: float
    page_number: int | None = None

    @classmethod
    def from_retrieved(cls, retrieved: RetrievedChunk) -> "SearchResult":
        chunk = retrieved.chunk
        document = retrieved.document
        return cls(
            chunk_id=chunk.id,
            document_id=document.id,
            filename=document.filename,
            original_filename=document.original_filename,
            content=chunk.original_content,
            similarity=round(retrieved.similarity, 6),
            page_number=chunk.metadata_.get("page_number"),
        )


class SearchResponse(BaseModel):
    """Response for a vector search request."""

    query: str
    results: list[SearchResult]