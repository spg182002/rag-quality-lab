import chromadb
import config
from chunker import load_documents, chunk_text


def expected_chunks():
    expected = {}
    for name, text in load_documents(config.DOCS_DIR).items():
        for i, chunk in enumerate(chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)):
            expected[f"{name}-{i}"] = chunk
    return expected


def stored_chunks():
    client = chromadb.PersistentClient(path=config.CHROMA_DIR)
    collection = client.get_collection(config.COLLECTION_NAME)
    data = collection.get()
    return dict(zip(data["ids"], data["documents"]))


def test_index_is_fresh():
    expected = expected_chunks()
    stored = stored_chunks()
    missing = sorted(set(expected) - set(stored))
    extra = sorted(set(stored) - set(expected))
    changed = sorted(i for i in expected if i in stored and expected[i] != stored[i])
    assert not (missing or extra or changed), (
        f"index is stale. missing={missing} extra={extra} changed={changed}"
    )