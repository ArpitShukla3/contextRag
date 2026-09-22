"""Document upload and management endpoints."""

from fastapi import APIRouter, Depends, File, UploadFile

from app.deps import get_document_service, get_ingestion_service
from app.schemas.chunk import ChunkRead
from app.schemas.document import DocumentRead
from app.services.documents import DocumentService
from app.services.ingestion import IngestionService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentRead, status_code=201)
def upload_document(
    file: UploadFile = File(...),
    service: IngestionService = Depends(get_ingestion_service),
) -> DocumentRead:
    """Upload a document and run the ingestion pipeline."""
    content = file.file.read()
    document = service.ingest(
        original_filename=file.filename or "",
        content_type=file.content_type or "",
        content=content,
    )
    return document


@router.get("", response_model=list[DocumentRead])
def list_documents(
    service: DocumentService = Depends(get_document_service),
) -> list[DocumentRead]:
    """List all documents, newest first."""
    return service.list_documents()


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: int,
    service: DocumentService = Depends(get_document_service),
) -> DocumentRead:
    """Return a single document by id."""
    return service.get_document(document_id)


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    service: DocumentService = Depends(get_document_service),
) -> None:
    """Delete a document and its chunks."""
    service.delete_document(document_id)


@router.get("/{document_id}/chunks", response_model=list[ChunkRead])
def list_document_chunks(
    document_id: int,
    service: DocumentService = Depends(get_document_service),
) -> list[ChunkRead]:
    """Return the chunks belonging to a document."""
    return service.list_chunks(document_id)