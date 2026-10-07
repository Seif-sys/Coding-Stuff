import os
import httpx

DEFAULT_MODEL = "claude-sonnet-5-5"


def complete(prompt: str, max_tokens: int = 500) -> str:
    if os.environ.get("LLM_PROVIDER") == "ollama":
        r = httpx.post(
            "http://localhost:11434/api/chat",
            json={
                "model": os.environ.get("LLM_MODEL", "llama3.2"),
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {"num_predict": max_tokens},
            },
            timeout=120,
        )
        r.raise_for_status()
        return r.json()["message"]["content"]

    import anthropic  # imported here so Ollama users never need a key
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=os.environ.get("LLM_MODEL", DEFAULT_MODEL),
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text