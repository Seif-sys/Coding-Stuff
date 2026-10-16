import json
import os
from typing import Iterator

import httpx

DEFAULT_MODEL = "llama3.2"
DEFAULT_URL = "http://localhost:11434"


def complete(prompt: str, max_tokens: int = 500) -> str:
    url = os.environ.get("OLLAMA_URL", DEFAULT_URL)
    model = os.environ.get("LLM_MODEL", DEFAULT_MODEL)
    try:
        r = httpx.post(
            f"{url}/api/chat",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                # temperature 0 = (near) deterministic answers, so eval runs are comparable
                "options": {"num_predict": max_tokens, "temperature": 0},
            },
            timeout=300,  # the first call is slow: the model has to load into memory
        )
    except httpx.ConnectError as exc:
        raise RuntimeError(f"Cannot reach Ollama at {url}. Is it running? (try: ollama serve)") from exc
    if r.status_code == 404:
        raise RuntimeError(f"Model '{model}' not found. Download it with: ollama pull {model}")
    r.raise_for_status()
    return r.json()["message"]["content"]

def stream(prompt: str, max_tokens: int = 500) -> Iterator[str]:
    url = os.environ.get("OLLAMA_URL", DEFAULT_URL)
    model = os.environ.get("LLM_MODEL", DEFAULT_MODEL)
    try:
        with httpx.stream(
            "POST",
            f"{url}/api/chat",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
                "options": {"num_predict": max_tokens, "temperature": 0},
            },
            timeout=300,
        ) as r:
            if r.status_code == 404:
                raise RuntimeError(f"Model '{model}' not found. Download it with: ollama pull {model}")
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                part = json.loads(line)
                piece = part.get("message", {}).get("content", "")
                if piece:
                    yield piece
                if part.get("done"):
                    break
    except httpx.ConnectError as exc:
        raise RuntimeError(f"Cannot reach Ollama at {url}. Is it running? (try: ollama serve)") from exc
