"""Chat schemas."""

from pydantic import BaseModel, Field

from app.services.retrieval import RetrievedChunk


class ChatRequest(BaseModel):
    """Payload for a retrieval-augmented chat request."""

    query: str = Field(min_length=1)
    top_k: int = Field(default=10, ge=1, le=50)
    stream: bool = Field(
        default=False, description="Stream the answer as Server-Sent Events."
    )


class ChatSource(BaseModel):
    """A context chunk the model was grounded on."""

    chunk_id: int
    document_id: int
    filename: str
    original_filename: str
    similarity: float
    snippet: str
    page_number: int | None = None

    @classmethod
    def from_retrieved(
        cls, retrieved: RetrievedChunk, snippet_chars: int = 200
    ) -> "ChatSource":
        chunk = retrieved.chunk
        document = retrieved.document
        content = chunk.original_content
        return cls(
            chunk_id=chunk.id,
            document_id=document.id,
            filename=document.filename,
            original_filename=document.original_filename,
            similarity=round(retrieved.similarity, 6),
            snippet=content[:snippet_chars],
            page_number=chunk.metadata_.get("page_number"),
        )


class ChatResponse(BaseModel):
    """Response for a non-streaming chat request."""

    answer: str
    sources: list[ChatSource]