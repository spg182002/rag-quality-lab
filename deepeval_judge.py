import requests
from deepeval.models import DeepEvalBaseLLM
import config


class OllamaJudge(DeepEvalBaseLLM):
    def __init__(self, model="llama3.1:8b"):
        self.model = model

    def load_model(self):
        return self.model

    def generate(self, prompt: str, schema=None):
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
        }
        r = requests.post(config.LLM_URL, json=payload, timeout=300)
        r.raise_for_status()
        text = r.json()["message"]["content"]
        if schema is not None:
            return schema.model_validate_json(text)
        return text

    async def a_generate(self, prompt: str, schema=None):
        return self.generate(prompt, schema)

    def get_model_name(self):
        return self.model