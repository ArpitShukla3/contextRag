"""Deterministic doubles for embedding and LLM providers (no network/model)."""

from __future__ import annotations

import hashlib
import math
import re

from app.core.config import get_settings
from app.services.embeddings import EmbeddingProvider
from app.services.llm import LLMProvider

_TOKENS = re.compile(r"\w+", re.UNICODE)


class FakeEmbeddingProvider(EmbeddingProvider):
    """Deterministic bag-of-words embeddings (no model, no network).

    Each word is hashed into a signed bucket; the unit vector is derived from
    the bag of words, so texts sharing vocabulary are cosine-similar and
    identical text produces similarity ``1.0``.
    """

    def __init__(self, dim: int | None = None) -> None:
        self._dim = dim or get_settings().embedding_dim

    def _vector(self, text: str) -> list[float]:
        coefficients = [0.0] * self._dim
        for token in _TOKENS.findall(text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], "big") % self._dim
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            coefficients[bucket] += sign
        norm = math.sqrt(sum(v * v for v in coefficients))
        if norm == 0.0:
            return [0.0] * self._dim
        return [v / norm for v in coefficients]

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]


class FakeLLMProvider(LLMProvider):
    """Canned LLM that records and replays every request."""

    def __init__(
        self,
        answer: str = "I found the answer in the context.",
        deltas: list[str] | None = None,
    ) -> None:
        self.answer_value = answer
        self.delta_values = deltas or ["I ", "found ", "the ", "answer."]
        self.requests: list[list[dict]] = []

    def complete(self, messages, *, temperature=0.3, max_tokens=1024) -> str:
        self.requests.append(messages)
        return self.answer_value

    def stream(self, messages, *, temperature=0.3, max_tokens=1024):
        self.requests.append(messages)
        return iter(self.delta_values)