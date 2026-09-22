"""Tests for the vector (pgvector) retriever."""

import pytest

from app.core.config import get_settings
from app.db.models import Chunk, Document, DocumentStatus
from app.services.retrieval import VectorRetriever
from tests.doubles import FakeEmbeddingProvider


def _seed_document(
    db_session,
) -> tuple[Document, list[Chunk]]:
    document = Document(
        filename="stored-doc.txt",
        original_filename="guide.txt",
        content_type="text/plain",
        file_size=10,
        status=DocumentStatus.PROCESSED,
    )
    db_session.add(document)
    db_session.flush()
    texts = [
        "Quantum computing exploits superposition to speed up certain problems.",
        "The capital of France is Paris and the Eiffel Tower is there.",
        "Rivers flow downhill because of gravity and the water cycle.",
    ]
    chunks = [
        Chunk(
            document_id=document.id,
            chunk_index=i,
            original_content=text,
            metadata_={"source": "guide.txt", "page_number": 1},
            embedding=FakeEmbeddingProvider().embed([text])[0],
        )
        for i, text in enumerate(texts)
    ]
    db_session.add_all(chunks)
    db_session.commit()
    return document, chunks


def test_retrieve_ranks_by_cosine_similarity(db_session):
    _, chunks = _seed_document(db_session)
    embeddings = FakeEmbeddingProvider()
    retriever = VectorRetriever(session=db_session, embedding_provider=embeddings)

    results = retriever.retrieve(chunks[1].original_content, top_k=3)

    assert results[0].chunk.id == chunks[1].id
    assert results[0].similarity == pytest.approx(1.0, abs=1e-6)
    assert results[0].document.id == chunks[1].document_id
    assert results[0].metadata["page_number"] == 1
    similarities = [r.similarity for r in results]
    assert similarities == sorted(similarities, reverse=True)


def test_retrieve_respects_top_k(db_session):
    _, chunks = _seed_document(db_session)
    retriever = VectorRetriever(
        session=db_session, embedding_provider=FakeEmbeddingProvider()
    )

    results = retriever.retrieve(chunks[0].original_content, top_k=2)

    assert len(results) == 2
    assert results[0].chunk.id == chunks[0].id


def test_retrieve_ignores_chunks_without_embeddings(db_session):
    document = Document(
        filename="no-embed.txt",
        original_filename="no-embed.txt",
        content_type="text/plain",
        file_size=4,
        status=DocumentStatus.PROCESSED,
    )
    db_session.add(document)
    db_session.commit()
    db_session.add(
        Chunk(
            document_id=document.id,
            chunk_index=0,
            original_content="Some text without an embedding.",
            metadata_={},
            embedding=None,
        )
    )
    db_session.commit()

    results = VectorRetriever(
        session=db_session, embedding_provider=FakeEmbeddingProvider()
    ).retrieve("Some text without an embedding.", top_k=5)

    assert results == []


def test_retrieve_with_nonpositive_top_k_returns_empty(db_session):
    _, chunks = _seed_document(db_session)
    retriever = VectorRetriever(
        session=db_session, embedding_provider=FakeEmbeddingProvider()
    )

    assert retriever.retrieve(chunks[0].original_content, top_k=0) == []


def test_fake_embedding_dimension_matches_config():
    vector = FakeEmbeddingProvider().embed(["hello"])[0]
    assert len(vector) == get_settings().embedding_dim