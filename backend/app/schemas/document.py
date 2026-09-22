"""Document schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.models import DocumentStatus


class DocumentBase(BaseModel):
    """Fields common to document requests and responses."""

    original_filename: str
    content_type: str
    file_size: int


class DocumentCreate(DocumentBase):
    """Payload for creating a document record."""

    filename: str


class DocumentRead(DocumentBase):
    """Document record returned to API clients."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime