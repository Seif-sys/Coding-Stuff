import json
import os
from typing import Iterator

import httpx

DEFAULT_MODEL = "llama-3.1-8b-instant"
URL = "https://api.groq.com/openai/v1/chat/completions"


def complete(prompt: str, max_tokens: int = 500) -> str:
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is not set. Create a free key at console.groq.com")
    model = os.environ.get("GROQ_MODEL", DEFAULT_MODEL)
    try:
        r = httpx.post(
            URL,
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0,
            },
            timeout=60,
        )
    except httpx.ConnectError as exc:
        raise RuntimeError("Cannot reach the Groq API. Check your internet connection.") from exc
    if r.status_code == 401:
        raise RuntimeError("Groq rejected the API key (401). Check GROQ_API_KEY.")
    if r.status_code == 429:
        raise RuntimeError("Groq rate limit reached (429). Wait a moment and retry.")
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def stream(prompt: str, max_tokens: int = 500) -> Iterator[str]:
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is not set. Create a free key at console.groq.com")
    model = os.environ.get("GROQ_MODEL", DEFAULT_MODEL)
    try:
        with httpx.stream(
            "POST",
            URL,
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0,
                "stream": True,
            },
            timeout=60,
        ) as r:
            if r.status_code == 401:
                raise RuntimeError("Groq rejected the API key (401). Check GROQ_API_KEY.")
            if r.status_code == 429:
                raise RuntimeError("Groq rate limit reached (429). Wait a moment and retry.")
            r.raise_for_status()
            for line in r.iter_lines():
                if not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if payload == "[DONE]":
                    break
                piece = json.loads(payload)["choices"][0]["delta"].get("content")
                if piece:
                    yield piece
    except httpx.ConnectError as exc:
        raise RuntimeError("Cannot reach the Groq API. Check your internet connection.") from exc
    