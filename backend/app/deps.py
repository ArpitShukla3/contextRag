"""Application dependency wiring."""

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.services.chat import ChatService
from app.services.chunking import TokenChunker
from app.services.documents import DocumentService
from app.services.embeddings import EmbeddingProvider, SentenceTransformerEmbeddingProvider
from app.services.ingestion import IngestionService
from app.services.llm import LLMProvider, OpenRouterProvider
from app.services.parsing import ParserRegistry, create_parser_registry
from app.services.retrieval import VectorRetriever
from app.services.search import SearchService
from app.services.storage import LocalDiskStorage
from app.services.validation import FileValidator


@lru_cache
def _get_storage() -> LocalDiskStorage:
    return LocalDiskStorage(get_settings().upload_dir)


def get_storage() -> LocalDiskStorage:
    """Dependency: singleton local-disk storage."""
    return _get_storage()


@lru_cache
def _get_embedding_provider() -> SentenceTransformerEmbeddingProvider:
    return SentenceTransformerEmbeddingProvider(get_settings().embedding_model)


def get_embedding_provider() -> EmbeddingProvider:
    """Dependency: singleton embedding provider (lazy model load)."""
    return _get_embedding_provider()


def get_parser_registry() -> ParserRegistry:
    """Dependency: parser registry with all built-in parsers."""
    return create_parser_registry()


def get_chunker() -> TokenChunker:
    """Dependency: configured token-aware chunker."""
    settings = get_settings()
    return TokenChunker(
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
    )


def get_file_validator() -> FileValidator:
    """Dependency: configured upload file validator."""
    settings = get_settings()
    allowed = set(get_parser_registry().suffixes())
    return FileValidator(
        allowed_suffixes=allowed,
        max_size_bytes=settings.max_upload_size_mb * 1024 * 1024,
    )


def get_ingestion_service(
    db: Session = Depends(get_db),
    embeddings: EmbeddingProvider = Depends(get_embedding_provider),
) -> IngestionService:
    """Dependency: ingestion pipeline service."""
    return IngestionService(
        session=db,
        storage=get_storage(),
        parser_registry=get_parser_registry(),
        chunker=get_chunker(),
        file_validator=get_file_validator(),
        embedding_provider=embeddings,
    )


def get_document_service(
    db: Session = Depends(get_db),
) -> DocumentService:
    """Dependency: document management service."""
    return DocumentService(
        session=db,
        storage=get_storage(),
    )


def get_llm_provider() -> LLMProvider:
    """Dependency: configured LLM provider."""
    settings = get_settings()
    return OpenRouterProvider(
        api_key=settings.openrouter_api_key,
        model=settings.openrouter_model,
        base_url=settings.openrouter_base_url,
    )


def get_vector_retriever(
    db: Session = Depends(get_db),
    embeddings: EmbeddingProvider = Depends(get_embedding_provider),
) -> VectorRetriever:
    """Dependency: pgvector semantic retriever."""
    return VectorRetriever(session=db, embedding_provider=embeddings)


def get_search_service(
    retriever: VectorRetriever = Depends(get_vector_retriever),
) -> SearchService:
    """Dependency: search orchestration service."""
    return SearchService(retriever=retriever)


def get_chat_service(
    retriever: VectorRetriever = Depends(get_vector_retriever),
    llm: LLMProvider = Depends(get_llm_provider),
) -> ChatService:
    """Dependency: retrieval-augmented chat service."""
    return ChatService(retriever=retriever, llm=llm)