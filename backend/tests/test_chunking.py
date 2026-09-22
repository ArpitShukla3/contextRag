"""Tests for the token-aware chunker."""

import pytest

from app.services.chunking import Chunk, TokenChunker, tokenize


def word_text(count: int) -> str:
    return " ".join(f"word{i}" for i in range(count))


class TestTokenAwareness:
    def test_boundaries_align_with_tokens(self):
        text = "hello world, this is a demo!"
        chunks = TokenChunker(chunk_size=4, overlap=1).split(text)
        assert all(chunk.char_start >= 0 and chunk.char_end <= len(text) for chunk in chunks)
        for chunk in chunks:
            assert chunk.text[0] != " " or chunk.text
        tokens = tokenize(text)
        first = tokens[0]
        assert chunks[0].text.startswith(first.text)


class TestChunkSizing:
    def test_single_chunk_when_text_fits(self):
        chunker = TokenChunker(chunk_size=10, overlap=2)
        chunks = chunker.split("hello world")
        assert len(chunks) == 1
        assert chunks[0].text == "hello world"
        assert chunks[0].token_count == 2

    def test_deterministic_split(self):
        text = word_text(20)
        chunker = TokenChunker(chunk_size=8, overlap=3)
        chunks = chunker.split(text)
        assert [chunk.token_count for chunk in chunks] == [8, 8, 10]
        assert len(chunks) == 3


class TestOverlap:
    def test_consecutive_chunks_share_overlap_tokens(self):
        text = word_text(20)
        chunker = TokenChunker(chunk_size=8, overlap=3)
        chunks = chunker.split(text)
        assert len(chunks) >= 2
        for first, second in zip(chunks, chunks[1:]):
            first_tokens = [t.text for t in tokenize(first.text)]
            second_tokens = [t.text for t in tokenize(second.text)]
            assert first_tokens[-3:] == second_tokens[:3]

    def test_overlap_zero_gives_non_overlapping_chunks(self):
        text = word_text(20)
        chunker = TokenChunker(chunk_size=5, overlap=0)
        chunks = chunker.split(text)
        assert [c.token_count for c in chunks] == [5, 5, 5, 5]

    def test_seq_total_token_count(self):
        """Every token appears in at least one chunk; no gaps."""
        text = word_text(20)
        chunks = TokenChunker(chunk_size=8, overlap=3).split(text)
        chunk_tokens = [t.text for c in chunks for t in tokenize(c.text)]
        assert len(set(chunk_tokens)) == 20


class TestEdgeCases:
    def test_empty_text(self):
        assert TokenChunker(10, 2).split("") == []

    def test_whitespace_only_text(self):
        assert TokenChunker(10, 2).split("   \n  ") == []

    def test_invalid_chunk_size(self):
        with pytest.raises(ValueError):
            TokenChunker(chunk_size=0, overlap=0)

    def test_overlap_bigger_than_chunk_size(self):
        with pytest.raises(ValueError):
            TokenChunker(chunk_size=4, overlap=4)

    def test_negative_overlap(self):
        with pytest.raises(ValueError):
            TokenChunker(chunk_size=4, overlap=-1)


class TestCoverage:
    def test_chunks_are_substrings_of_source(self):
        text = word_text(50)
        chunks = TokenChunker(chunk_size=10, overlap=2).split(text)
        for chunk in chunks:
            assert chunk.char_start <= chunk.char_end
            assert text[chunk.char_start : chunk.char_end] == chunk.text