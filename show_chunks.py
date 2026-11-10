from chunker import load_documents, chunk_text
import config

text = load_documents(config.DOCS_DIR)["travel_allowance.txt"]
for i, c in enumerate(chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)):
    print(f"--- chunk {i} ---")
    print(c)