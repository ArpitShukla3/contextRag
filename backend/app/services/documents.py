"""Document query and management service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import Document
from app.exceptions import NotFoundError
from app.repositories.chunks import ChunkRepository
from app.repositories.documents import DocumentRepository
from app.services.storage import Storage


class DocumentService:
    """Queries and lifecycle operations for stored documents."""

    def __init__(
        self,
        session: Session,
        *,
        storage: Storage,
    ) -> None:
        self._session = session
        self._storage = storage
        self._documents = DocumentRepository(session)
        self._chunks = ChunkRepository(session)

    def list_documents(self) -> list[Document]:
        return self._documents.list()

    def get_document(self, document_id: int) -> Document:
        document = self._documents.get(document_id)
        if document is None:
            raise NotFoundError(f"Document {document_id} not found.")
        return document

    def delete_document(self, document_id: int) -> None:
        document = self.get_document(document_id)
        try:
            self._storage.delete(document.filename)
            self._documents.delete(document)
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

    def list_chunks(self, document_id: int):
        self.get_document(document_id)
        return self._chunks.list_by_document(document_id)