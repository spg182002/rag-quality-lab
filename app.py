import requests
import config
from retrieve import retrieve
import re

def load_prompt():
    with open(config.PROMPT_FILE, encoding="utf-8") as f:
        return f.read()


def build_messages(question, chunks):
    context = "\n\n".join(c["text"] for c in chunks)
    system = load_prompt() + "\n\nDocuments:\n" + context
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": question},
    ]


def ask(question):
    
    chunks = retrieve(question)
    payload = {
        "model": config.LLM_MODEL,
        "messages": build_messages(question, chunks),
        "stream": False,
        "options": {"temperature": config.TEMPERATURE},
    }
    response = requests.post(config.LLM_URL, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    return {
        "question": question,
        "retrieved_chunks": chunks,
        "answer": filter_output(data["message"]["content"]),
        "done_reason": data["done_reason"],
    }


if __name__ == "__main__":
    questions = [
        "How many sick days do I get?",
        "What is the notice period?",
        "What is the maternity leave policy?",
    ]
    for q in questions:
        result = ask(q)
        print("\nQUESTION:", result["question"])
        print("ANSWER:  ", result["answer"])
        print("DONE:    ", result["done_reason"])
        print("CHUNKS:  ", [c["chunk_index"] for c in result["retrieved_chunks"]])

def filter_output(answer):
    answer = re.sub(r"\b\d{3}-\d{4}\b", "[redacted]", answer)
    answer = re.sub(r"(?i)\bvisit\s+\S+\.example\.com\b", "", answer)
    return answer.strip()

