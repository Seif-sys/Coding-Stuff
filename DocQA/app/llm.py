import os

import anthropic

DEFAULT_MODEL = "claude-sonnet-5-5"


def complete(prompt: str, max_tokens: int = 500) -> str:
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=os.environ.get("LLM_MODEL", DEFAULT_MODEL),
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text