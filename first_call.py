import requests

URL = "http://localhost:11434/api/chat"

payload = {
    "model": "llama3.2:3b",
    "messages": [
        {"role": "system", "content": "Answer in one short sentence."},
        {"role": "user", "content": "How many days of sick leave do employees get?"},
    ],
    "stream": False,
    "options": {"temperature": 0, "num_predict": 15},
}

response = requests.post(URL, json=payload, timeout=120)
response.raise_for_status()
data = response.json()

print("Answer:", data["message"]["content"])
print("done_reason:", data["done_reason"])