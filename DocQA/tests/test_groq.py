import pytest
from app.llm import groq


class FakeResponse:
    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self._data = data or {}

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_complete_returns_text(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test")
    monkeypatch.setattr(
        groq.httpx, "post",
        lambda url, **kw: FakeResponse(data={"choices": [{"message": {"content": "Bremen"}}]}),
    )
    assert groq.complete("Where?") == "Bremen"


def test_missing_key_raises(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        groq.complete("x")


def test_rate_limit_message(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test")
    monkeypatch.setattr(groq.httpx, "post", lambda url, **kw: FakeResponse(status_code=429))
    with pytest.raises(RuntimeError, match="rate limit"):
        groq.complete("x")


def test_factory_selects_groq(monkeypatch):
    from app import llm
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    assert llm.get_provider() is groq
    