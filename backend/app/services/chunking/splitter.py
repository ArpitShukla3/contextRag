"""Approximate token-aware text splitter.

Keeps chunk boundaries on token boundaries using a lightweight approximate
tokenizer rather than blindly slicing characters.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    """A token with its character span in the source text."""

    text: str
    start: int
    end: int


@dataclass(frozen=True)
class Chunk:
    """A produced chunk referencing the original text."""

    text: str
    token_count: int
    char_start: int
    char_end: int


_TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def tokenize(text: str) -> list[Token]:
    """Tokenize text into word/punctuation tokens with character spans."""
    return [
        Token(text=match.group(), start=match.start(), end=match.end())
        for match in _TOKEN_RE.finditer(text)
    ]


class TokenChunker:
    """Split text into overlapping, token-bounded chunks."""

    def __init__(self, chunk_size: int, overlap: int) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer.")
        if not 0 <= overlap < chunk_size:
            raise ValueError("overlap must be >= 0 and smaller than chunk_size.")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, text: str) -> list[Chunk]:
        """Split ``text`` into chunks of at most ``chunk_size`` tokens."""
        tokens = tokenize(text)
        if not tokens:
            return []

        token_count = len(tokens)
        if token_count <= self.chunk_size:
            return [
                Chunk(
                    text=text,
                    token_count=token_count,
                    char_start=0,
                    char_end=len(text),
                )
            ]

        stride = self.chunk_size - self.overlap
        chunks: list[Chunk] = []
        start = 0

        while start < token_count:
            end = min(start + self.chunk_size, token_count)
            if token_count - end <= self.overlap:
                end = token_count

            first = tokens[start]
            last = tokens[end - 1]
            chunks.append(
                Chunk(
                    text=text[first.start : last.end],
                    token_count=end - start,
                    char_start=first.start,
                    char_end=last.end,
                )
            )

            if end == token_count:
                break
            start += stride

        return chunks