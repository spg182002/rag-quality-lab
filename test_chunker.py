import config
from chunker import load_documents, chunk_text
import pytest


def test_overlap_must_be_smaller_than_size():
    with pytest.raises(ValueError):
        chunk_text("some text", 100, 100)


def test_no_chunk_exceeds_size():
    for text in load_documents(config.DOCS_DIR).values():
        for c in chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP):
            assert len(c) <= config.CHUNK_SIZE


def test_no_tiny_fragment_chunk():
    for text in load_documents(config.DOCS_DIR).values():
        chunks = chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        assert len(chunks[-1]) > config.CHUNK_OVERLAP


def test_notice_period_is_whole_in_some_chunk():
    text = load_documents(config.DOCS_DIR)["leave_policy.txt"]
    chunks = chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    assert any("30 days written notice" in c for c in chunks)