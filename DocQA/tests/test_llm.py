"""Tests for the Ollama wrapper. httpx.post is faked: no Ollama needed."""
import httpx
import pytest

from app import llm


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=None, response=None)

    def json(self):
        return self._payload


def test_complete_sends_request_and_returns_text(monkeypatch):
    seen = {}

    def fake_post(url, json, timeout):
        seen["url"], seen["json"] = url, json
        return FakeResponse(payload={"message": {"content": "Bremen"}})

    monkeypatch.setattr(llm.httpx, "post", fake_post)
    monkeypatch.setenv("OLLAMA_URL", "http://example:1234")
    monkeypatch.setenv("LLM_MODEL", "tiny")
    assert llm.complete("Where?") == "Bremen"
    assert seen["url"] == "http://example:1234/api/chat"
    assert seen["json"]["model"] == "tiny"
    assert seen["json"]["messages"][0]["content"] == "Where?"
    assert seen["json"]["stream"] is False


def test_complete_explains_connection_error(monkeypatch):
    def fake_post(url, json, timeout):
        raise httpx.ConnectError("refused")

    monkeypatch.setattr(llm.httpx, "post", fake_post)
    with pytest.raises(RuntimeError, match="Is it running"):
        llm.complete("x")


def test_complete_explains_missing_model(monkeypatch):
    monkeypatch.setattr(llm.httpx, "post", lambda url, json, timeout: FakeResponse(status_code=404))
    with pytest.raises(RuntimeError, match="ollama pull"):
        llm.complete("x")
