from pathlib import Path
import config


def load_documents(folder):
    docs = {}
    for path in Path(folder).glob("*.txt"):
        docs[path.name] = path.read_text(encoding="utf-8")
    return docs


def chunk_text(text, size, overlap):
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    step = size - overlap
    chunks = []

    for start in range(0, len(text), step):
        piece = text[start:start + size]
        if piece.strip():
            chunks.append(piece)
        if start + size >= len(text):
            break
    return chunks


if __name__ == "__main__":
    docs = load_documents(config.DOCS_DIR)
    for name, text in docs.items():
        chunks = chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        print(f"{name}: {len(text)} chars -> {len(chunks)} chunks")
        for i, c in enumerate(chunks):
            print(f"--- chunk {i} ---")
            print(repr(c))