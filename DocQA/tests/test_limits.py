from fastapi.testclient import TestClient

from app.main import app
from app.ratelimit import RateLimiter

client = TestClient(app)
FAKE_PDF = b"%PDF-1.4 fake"


def upload(monkeypatch, pages=("Some text.",)):
    monkeypatch.setattr("app.main.pdf.extract_pages", lambda d: list(pages))
    return client.post("/documents", files={"file": ("a.pdf", FAKE_PDF, "application/pdf")})


def test_question_too_long_is_422():
    r = client.post("/ask", json={"question": "q" * 1001, "text": "t"})
    assert r.status_code == 422


def test_too_many_doc_ids_is_422():
    r = client.post("/ask", json={"question": "q?", "doc_ids": [str(i) for i in range(11)]})
    assert r.status_code == 422


def test_document_cap_is_409(monkeypatch):
    monkeypatch.setattr("app.main.MAX_DOCS", 1)
    assert upload(monkeypatch).status_code == 201
    r = upload(monkeypatch)
    assert r.status_code == 409
    assert "limit" in r.json()["detail"].lower()


def test_page_cap_is_413(monkeypatch):
    monkeypatch.setattr("app.main.MAX_PAGES", 1)
    assert upload(monkeypatch, pages=("a", "b")).status_code == 413


def test_rate_limit_returns_429(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_MIN", "2")
    monkeypatch.setattr("app.llm.complete", lambda p, max_tokens=500: "ok")
    body = {"question": "q?", "text": "t"}
    assert client.post("/ask", json=body).status_code == 200
    assert client.post("/ask", json=body).status_code == 200
    r = client.post("/ask", json=body)
    assert r.status_code == 429
    assert r.headers["retry-after"] == "60"
    assert client.get("/health").status_code == 200  # health is never limited


def test_rate_limit_can_be_disabled(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_MIN", "0")
    monkeypatch.setattr("app.llm.complete", lambda p, max_tokens=500: "ok")
    for _ in range(5):
        assert client.post("/ask", json={"question": "q?", "text": "t"}).status_code == 200


def test_limiter_window_expires():
    rl = RateLimiter()
    assert rl.allow("ip", limit=1, window=60, now=0)
    assert not rl.allow("ip", limit=1, window=60, now=30)
    assert rl.allow("ip", limit=1, window=60, now=61)  # old hit fell out of the window