"""Sentence-Transformer based embedding provider."""

from app.services.embeddings.base import EmbeddingProvider

try:
    from sentence_transformers import SentenceTransformer
except ImportError as exc:  # pragma: no cover - dependency missing
    raise ImportError(
        "sentence-transformers is required for embeddings."
    ) from exc


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """Embeddings via a Hugging Face sentence-transformers model.

    The model is loaded lazily on first use. Output vectors are L2-normalized
    so cosine similarity equals the dot product in pgvector.
    """

    def __init__(self, model_name: str, model=None) -> None:
        self._model_name = model_name
        self._model = model

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self._model_name)
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        model = self._get_model()
        vectors = model.encode(
            list(texts),
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return vectors.tolist()