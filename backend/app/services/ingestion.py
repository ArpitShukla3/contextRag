"""Document ingestion pipeline: upload, parse, chunk, persist."""

from __future__ import annotations

from pathlib import PurePath
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.models import Document, DocumentStatus
from app.exceptions import AppError, FileValidationError, ProcessingError
from app.repositories.chunks import ChunkDraft, ChunkRepository
from app.repositories.documents import DocumentRepository
from app.services.chunking import TokenChunker
from app.services.embeddings import EmbeddingProvider
from app.services.parsing import ParserRegistry
from app.services.storage import Storage
from app.services.validation import FileValidator

logger = get_logger(__name__)


class IngestionService:
    """Orchestrates the file -> validation -> parse -> chunk -> database pipeline."""

    def __init__(
        self,
        session: Session,
        *,
        storage: Storage,
        parser_registry: ParserRegistry,
        chunker: TokenChunker,
        file_validator: FileValidator,
        embedding_provider: EmbeddingProvider,
    ) -> None:
        self._session = session
        self._storage = storage
        self._parsers = parser_registry
        self._chunker = chunker
        self._validator = file_validator
        self._embeddings = embedding_provider
        self._documents = DocumentRepository(session)
        self._chunks = ChunkRepository(session)

    def ingest(
        self,
        *,
        original_filename: str,
        content_type: str,
        content: bytes,
    ) -> Document:
        self._validator.validate(
            original_filename=original_filename, content=content
        )

        parser = self._parsers.get_for_suffix(original_filename)
        if parser is None:
            raise FileValidationError(
                f"No parser available for {original_filename!r}."
            )

        storage_name = f"{uuid4().hex}{PurePath(original_filename).suffix.lower()}"
        self._storage.save(storage_name, content)

        document = self._documents.create(
            filename=storage_name,
            original_filename=original_filename,
            content_type=content_type or "application/octet-stream",
            file_size=len(content),
        )
        self._documents.set_status(document, DocumentStatus.PROCESSING)
        self._session.commit()

        try:
            parsed = parser.parse(content)
            if parsed.is_empty:
                raise FileValidationError(
                    "The document contains no extractable text."
                )

            drafts = self._chunk_parsed_document(parsed, original_filename)
            if not drafts:
                raise FileValidationError(
                    "The document contains no extractable text."
                )

            chunk_rows = self._chunks.bulk_insert(document.id, drafts)
            embeddings = self._embeddings.embed(
                [draft.original_content for draft in drafts]
            )
            for row, embedding in zip(chunk_rows, embeddings):
                row.embedding = embedding
            self._documents.set_status(document, DocumentStatus.PROCESSED)
        except AppError as exc:
            self._mark_failed(document, exc)
            raise
        except Exception as exc:
            self._mark_failed(
                document, ProcessingError("Failed to process document."), from_exc=exc
            )
            raise

        self._session.commit()
        logger.info(
            "Document processed: id=%s name=%r chunks=%d",
            document.id,
            original_filename,
            len(drafts),
        )
        return document

    def _chunk_parsed_document(
        self, parsed, original_filename: str
    ) -> list[ChunkDraft]:
        drafts: list[ChunkDraft] = []
        chunk_index = 0
        for page in parsed.pages:
            for chunk in self._chunker.split(page.text):
                metadata = {"source": original_filename}
                if page.page_number is not None:
                    metadata["page_number"] = page.page_number
                drafts.append(
                    ChunkDraft(
                        chunk_index=chunk_index,
                        original_content=chunk.text,
                        metadata=metadata,
                    )
                )
                chunk_index += 1
        return drafts

    def _mark_failed(self, document: Document, exc: AppError, *, from_exc=None) -> None:
        self._documents.set_status(document, DocumentStatus.FAILED)
        self._session.commit()
        if from_exc is not None:
            logger.exception(
                "Document failed: id=%s name=%r", document.id, document.original_filename
            )
        else:
            logger.warning(
                "Document failed validation: id=%s name=%r error=%s",
                document.id,
                document.original_filename,
                exc.message,
            )