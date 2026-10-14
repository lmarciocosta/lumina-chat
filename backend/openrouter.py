import os
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "nvidia/nemotron-3.5-lightning:free"


def _get_api_key() -> str:
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    api_key = (os.getenv("OPENROUTER_API_KEY") or "").strip().strip('"')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY vazia. Salve a chave no arquivo .env")
    return api_key


def send_message_to_openrouter(message: str, model: str = DEFAULT_MODEL) -> str:
    response = requests.post(
        OPENROUTER_URL,
        headers={"Authorization": f"Bearer {_get_api_key()}"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": message}],
        },
        timeout=120,
    )
    data = response.json()
    if not response.ok:
        error = data.get("error")
        if isinstance(error, dict):
            raise RuntimeError(error.get("message", str(error)))
        raise RuntimeError(str(error or data))
    if "choices" not in data:
        raise RuntimeError(str(data.get("error", data)))
    return data["choices"][0]["message"]["content"]
