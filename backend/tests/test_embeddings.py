"""Tests for the sentence-transformers embedding provider."""

import math

import numpy as np

from app.services.embeddings import SentenceTransformerEmbeddingProvider


class StubModel:
    """Replaces SentenceTransformer so tests need no model download."""

    def __init__(self) -> None:
        self.received_texts: list[str] = []

    def encode(self, texts, *, normalize_embeddings=True, convert_to_numpy=True):
        self.received_texts = list(texts)
        matrix = np.array([[float(i), 1.0, 0.0] for i in range(len(texts))])
        if normalize_embeddings:
            norms = np.linalg.norm(matrix, axis=1, keepdims=True)
            matrix = matrix / norms
        return matrix


def test_provider_uses_injected_model():
    stub = StubModel()
    provider = SentenceTransformerEmbeddingProvider("fake-model", model=stub)

    vectors = provider.embed(["alpha", "beta"])

    assert stub.received_texts == ["alpha", "beta"]
    assert len(vectors) == 2
    assert all(len(v) == 3 for v in vectors)


def test_provider_normalizes_embeddings():
    stub = StubModel()
    provider = SentenceTransformerEmbeddingProvider("fake-model", model=stub)

    vectors = provider.embed(["alpha", "beta"])

    for vector in vectors:
        assert math.isclose(
            math.sqrt(sum(x * x for x in vector)), 1.0, abs_tol=1e-6
        )


def test_provider_empty_batch_returns_empty_list():
    provider = SentenceTransformerEmbeddingProvider("fake-model", model=StubModel())
    assert provider.embed([]) == []


def test_embed_one_matches_batch():
    stub = StubModel()
    provider = SentenceTransformerEmbeddingProvider("fake-model", model=stub)
    assert provider.embed_one("alpha") == provider.embed(["alpha"])[0]