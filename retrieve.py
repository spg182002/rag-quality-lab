import chromadb
import config
from store import embed


def retrieve(question, k=None):
    if k is None:
        k = config.TOP_K
    client = chromadb.PersistentClient(path=config.CHROMA_DIR)
    collection = client.get_collection(config.COLLECTION_NAME)
    result = collection.query(query_embeddings=embed([question]), n_results=k)

    chunks = []
    for text, dist, meta in zip(
        result["documents"][0], result["distances"][0], result["metadatas"][0]
    ):
        chunks.append({
            "text": text,
            "distance": round(dist, 3),
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
        })
    return chunks


if __name__ == "__main__":
    questions = [
        "How many sick days do I get?",
        "What is the notice period?",
        "What is the maternity leave policy?",
    ]
    for q in questions:
        print("\nQUESTION:", q)
        for c in retrieve(q):
            print(f"  chunk {c['chunk_index']}  distance={c['distance']}  {c['text'][:50]!r}")