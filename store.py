import chromadb
import requests
import config
from chunker import load_documents, chunk_text


def embed(texts):
    payload = {"model": config.EMBED_MODEL, "input": texts}
    response = requests.post(config.EMBED_URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()["embeddings"]


def build_index():
    client = chromadb.PersistentClient(path=config.CHROMA_DIR)
    try:
        client.delete_collection(config.COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        name=config.COLLECTION_NAME,
        configuration={"hnsw": {"space": "cosine"}},
    )

    ids, texts, metas = [], [], []
    for name, text in load_documents(config.DOCS_DIR).items():
        for i, chunk in enumerate(chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)):
            ids.append(f"{name}-{i}")
            texts.append(chunk)
            metas.append({"source": name, "chunk_index": i})

    collection.add(ids=ids, documents=texts, embeddings=embed(texts), metadatas=metas)
    return collection


if __name__ == "__main__":
    col = build_index()
    print("Chunks stored:", col.count())