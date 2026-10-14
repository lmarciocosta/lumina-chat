"""Testa a chave do .env contra a API do OpenRouter (não imprime a chave)."""
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "nvidia/nemotron-3.5-lightning:free"

key = (os.getenv("OPENROUTER_API_KEY") or "").strip().strip('"')
if not key:
    raise SystemExit("OPENROUTER_API_KEY vazia no .env")
print(f"Chave carregada: sim ({len(key)} caracteres, começa com {key[:8]}...)")

response = requests.post(
    OPENROUTER_URL,
    headers={"Authorization": f"Bearer {key}"},
    json={"model": DEFAULT_MODEL, "messages": [{"role": "user", "content": "ping"}]},
    timeout=60,
)
print(f"HTTP {response.status_code}")
data = response.json()
if response.ok and "choices" in data:
    print("OK — OpenRouter aceitou a chave.")
else:
    err = data.get("error", data)
    print("Erro OpenRouter:", err if isinstance(err, str) else err.get("message", err))
