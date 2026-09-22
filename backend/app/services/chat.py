"""Chat orchestration: retrieve context, build prompt, call the LLM."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from app.db.models import Chunk, Document
from app.services.llm import LLMProvider
from app.services.prompting import ContextEntry, PromptBuilder
from app.services.retrieval import RetrievedChunk, VectorRetriever


@dataclass(frozen=True)
class ChatAnswer:
    """A completed chat response with its retrieved context."""

    answer: str
    chunks: list[RetrievedChunk]


@dataclass(frozen=True)
class ChatStream:
    """A streaming chat response. Retrieval runs eagerly; deltas stream lazily."""

    deltas: Iterator[str]
    chunks: list[RetrievedChunk]


def _source_label(document: Document, chunk: Chunk) -> str:
    label = document.original_filename
    page_number = chunk.metadata_.get("page_number")
    if page_number is not None:
        label = f"{label} (page {page_number})"
    return label


class ChatService:
    def __init__(
        self,
        retriever: VectorRetriever,
        llm: LLMProvider,
        prompt_builder: PromptBuilder | None = None,
    ) -> None:
        self._retriever = retriever
        self._llm = llm
        self._prompt_builder = prompt_builder or PromptBuilder()

    def _prepare(self, query: str, top_k: int) -> tuple[list[ContextEntry], list[RetrievedChunk]]:
        retrieved = self._retriever.retrieve(query, top_k)
        entries = [
            ContextEntry(
                index=i + 1,
                content=result.chunk.original_content,
                source=_source_label(result.document, result.chunk),
            )
            for i, result in enumerate(retrieved)
        ]
        return entries, retrieved

    def answer(self, query: str, top_k: int = 10) -> ChatAnswer:
        entries, retrieved = self._prepare(query, top_k)
        messages = self._prompt_builder.build_messages(query=query, entries=entries)
        text = self._llm.complete(messages)
        return ChatAnswer(answer=text, chunks=retrieved)

    def stream(self, query: str, top_k: int = 10) -> ChatStream:
        entries, retrieved = self._prepare(query, top_k)
        messages = self._prompt_builder.build_messages(query=query, entries=entries)
        deltas = self._llm.stream(messages)
        return ChatStream(deltas=deltas, chunks=retrieved)