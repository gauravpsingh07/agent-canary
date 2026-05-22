import pytest

from agent_canary.services.chunking import chunk_text, normalize_text


def test_normalize_text_collapses_spacing_without_erasing_paragraphs() -> None:
    text = " First\tline.  \r\n\r\n\r\nSecond   line. "

    assert normalize_text(text) == "First line.\n\nSecond line."


def test_chunk_text_creates_overlapping_chunks() -> None:
    text = " ".join(f"word{i}" for i in range(40))

    chunks = chunk_text(text, max_chars=80, overlap_chars=12)

    assert len(chunks) > 1
    assert chunks[0].chunk_index == 0
    assert chunks[1].char_start < chunks[0].char_end
    assert all(chunk.token_count > 0 for chunk in chunks)


def test_chunk_text_rejects_invalid_overlap() -> None:
    with pytest.raises(ValueError, match="overlap_chars"):
        chunk_text("hello world", max_chars=10, overlap_chars=10)
