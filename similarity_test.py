import requests

URL = "http://localhost:11434/api/embed"


def embed(text):
    payload = {"model": "nomic-embed-text", "input": text}
    response = requests.post(URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()["embeddings"][0]


def similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    len_a = sum(x * x for x in a) ** 0.5
    len_b = sum(y * y for y in b) ** 0.5
    return dot / (len_a * len_b)


fact = embed("Every full-time employee gets 10 sick days per year.")
similar = embed("How many sick days do employees get?")
unrelated = embed("The office cafeteria serves lunch at noon.")

print("fact vs similar question:", round(similarity(fact, similar), 3))
print("fact vs unrelated:       ", round(similarity(fact, unrelated), 3))