"""Document data access."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Document, DocumentStatus


class DocumentRepository:
    """Data-access operations for the ``documents`` table."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        filename: str,
        original_filename: str,
        content_type: str,
        file_size: int,
        status: DocumentStatus = DocumentStatus.UPLOADED,
    ) -> Document:
        document = Document(
            filename=filename,
            original_filename=original_filename,
            content_type=content_type,
            file_size=file_size,
            status=status,
        )
        self._session.add(document)
        self._session.flush()
        return document

    def get(self, document_id: int) -> Document | None:
        return self._session.get(Document, document_id)

    def list(self) -> list[Document]:
        statement = select(Document).order_by(
            Document.created_at.desc(), Document.id.desc()
        )
        return list(self._session.scalars(statement).all())

    def delete(self, document: Document) -> None:
        self._session.delete(document)
        self._session.flush()

    def set_status(self, document: Document, status: DocumentStatus) -> None:
        document.status = status