"""Embedding provider subsystem (pluggable backends)."""

from app.services.embeddings.base import EmbeddingProvider
from app.services.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddingProvider,
)

__all__ = ["EmbeddingProvider", "SentenceTransformerEmbeddingProvider"]