import os

import httpx  # noqa: F401  (tests patch llm.httpx.post)


def get_provider():
    name = os.environ.get("LLM_PROVIDER", "ollama")
    if name == "ollama":
        from . import ollama
        return ollama
    if name == "groq":
            from . import groq
            return groq
    raise ValueError(f"Unknown LLM_PROVIDER: {name!r}")


def complete(prompt: str, max_tokens: int = 500) -> str:
    return get_provider().complete(prompt, max_tokens)