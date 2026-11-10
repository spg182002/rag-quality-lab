import requests

URL = "http://localhost:11434/api/embed"

payload = {
    "model": "nomic-embed-text",
    "input": "Every full-time employee gets 10 sick days per year.",
}

response = requests.post(URL, json=payload, timeout=120)
response.raise_for_status()
data = response.json()

vector = data["embeddings"][0]

print("Vector length:", len(vector))
print("First 5 numbers:", vector[:5])