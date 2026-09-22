"""Prompt construction for retrieval-augmented generation."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_SYSTEM_INSTRUCTIONS = (
    "You are a precise question-answering assistant. Answer the user's "
    "question using ONLY the retrieved context provided under 'Context'. "
    "Do not invent facts, details, or sources that are not present in the "
    "context. If the context does not contain enough information to answer, "
    "state explicitly that the information is unavailable. "
    "When you rely on a context excerpt, cite it as [n], where n is the "
    "excerpt number shown next to that excerpt."
)


@dataclass(frozen=True)
class ContextEntry:
    """A numbered context excerpt presented to the model."""

    index: int
    content: str
    source: str


def format_context(entries: list[ContextEntry]) -> str:
    """Render context entries as a numbered, sourced block."""
    rendered: list[str] = []
    for entry in entries:
        rendered.append(f"[{entry.index}] (source: {entry.source})\n{entry.content}")
    return "\n\n".join(rendered)


class PromptBuilder:
    """Builds OpenAI-style messages with clearly separated sections."""

    def __init__(self, system_instructions: str = DEFAULT_SYSTEM_INSTRUCTIONS) -> None:
        self._system_instructions = system_instructions

    def build_messages(
        self,
        *,
        query: str,
        entries: list[ContextEntry],
    ) -> list[dict]:
        """Return ``[{system}, {user}]`` messages for the given context + question."""
        user_content = f"Context:\n\n{format_context(entries)}\n\nQuestion: {query}"
        return [
            {"role": "system", "content": self._system_instructions},
            {"role": "user", "content": user_content},
        ]