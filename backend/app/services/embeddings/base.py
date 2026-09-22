"""Embedding provider abstraction."""

from __future__ import annotations

import abc


class EmbeddingProvider(abc.ABC):
    """Contract for turning text into vector embeddings."""

    @abc.abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts into vectors of equal dimensionality."""

    def embed_one(self, text: str) -> list[float]:
        """Embed a single text into a vector."""
        batch = self.embed([text])
        if not batch:
            raise ValueError("Embedding provider returned no vectors.")
        return batch[0]