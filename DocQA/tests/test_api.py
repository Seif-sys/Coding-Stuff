from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"ok": True}


def test_ask_returns_llm_answer(monkeypatch):
    seen = {}

    def fake_complete(prompt, max_tokens=500):
        seen["prompt"] = prompt
        return "42"

    monkeypatch.setattr("app.llm.complete", fake_complete)
    r = client.post("/ask", json={"question": "What is x?", "text": "x is 42."})
    assert r.status_code == 200
    assert r.json() == {"answer": "42"}
    assert "x is 42" in seen["prompt"]  # retrieved context really reached the prompt


def test_ask_validates_input():
    r = client.post("/ask", json={"question": "", "text": "abc"})
    assert r.status_code == 422  # rejected by pydantic before any LLM call


def test_ask_reports_llm_failure(monkeypatch):
    def boom(prompt, max_tokens=500):
        raise RuntimeError("no key")

    monkeypatch.setattr("app.llm.complete", boom)
    r = client.post("/ask", json={"question": "q?", "text": "t"})
    assert r.status_code == 502


def test_ask_tiny_input_does_not_crash_retrieval(monkeypatch):
    monkeypatch.setattr("app.llm.complete", lambda p, max_tokens=500: "ok")
    r = client.post("/ask", json={"question": "q?", "text": "t"})
    assert r.status_code == 200
