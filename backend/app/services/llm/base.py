"""LLM provider abstraction."""

from __future__ import annotations

import abc
from collections.abc import Iterator


class LLMProvider(abc.ABC):
    """Contract for chat completion providers."""

    @abc.abstractmethod
    def complete(
        self,
        messages: list[dict],
        *,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        """Return a full completion for ``messages``.

        ``messages`` is an OpenAI-style list of ``{"role": ..., "content": ...}``.
        """

    @abc.abstractmethod
    def stream(
        self,
        messages: list[dict],
        *,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> Iterator[str]:
        """Yield completion content deltas for ``messages`` as they arrive."""