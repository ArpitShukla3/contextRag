"""Chunk schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChunkRead(BaseModel):
    """Chunk record returned to API clients (embedding excluded)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    chunk_index: int
    original_content: str
    contextual_content: str | None = None
    metadata: dict[str, Any] = Field(
        default_factory=dict, validation_alias="metadata_"
    )
    created_at: datetime