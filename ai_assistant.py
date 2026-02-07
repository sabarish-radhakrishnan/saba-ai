# ai_assistant.py
import requests

SYSTEM_PROMPT = "You are Saba, a helpful browser assistant. Be concise and practical."

class BrowserAI:
    name = "Saba"
    version = "BrowserAI-1.0"

    def __init__(self, model="llama3.1", url="http://localhost:11434/api/chat"):
        self.model = model
        self.url = url

    def process_input(self, text: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            "stream": False
        }
        r = requests.post(self.url, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["message"]["content"]
