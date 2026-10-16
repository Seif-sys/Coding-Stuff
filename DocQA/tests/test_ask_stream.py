import json

import pytest
from fastapi.testclient import TestClient

from app.documents import Chunk, store
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_store():
    store.clear()
    yield
    store.clear()


def parse_sse(body: str):
    events = []
    for block in body.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in block.splitlines())
        events.append((lines["event"], json.loads(lines["data"])))
    return events


def test_stream_docs_sends_sources_tokens_done(monkeypatch):
    monkeypatch.setattr("app.llm.stream", lambda p, max_tokens=500: iter(["Bre", "men"]))
    d = store.add("b.pdf", [Chunk("Bremen lies on the Weser.", 7)])
    r = client.post("/ask/stream", json={"question": "Which city?", "doc_ids": [d.id], "k": 1})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")
    events = parse_sse(r.text)
    assert [e for e, _ in events] == ["sources", "token", "token", "done"]
    assert events[0][1][0]["page"] == 7
    assert "".join(d for e, d in events if e == "token") == "Bremen"


def test_stream_text_mode_has_no_sources(monkeypatch):
    monkeypatch.setattr("app.llm.stream", lambda p, max_tokens=500: iter(["42"]))
    r = client.post("/ask/stream", json={"question": "What is x?", "text": "x is 42."})
    assert [e for e, _ in parse_sse(r.text)] == ["token", "done"]


def test_stream_unknown_doc_is_404():
    r = client.post("/ask/stream", json={"question": "q?", "doc_ids": ["nope"]})
    assert r.status_code == 404


def test_stream_midway_failure_sends_error_event(monkeypatch):
    def broken(prompt, max_tokens=500):
        yield "Br"
        raise RuntimeError("connection lost")

    monkeypatch.setattr("app.llm.stream", broken)
    r = client.post("/ask/stream", json={"question": "q?", "text": "some text"})
    kinds = [e for e, _ in parse_sse(r.text)]
    assert kinds == ["token", "error"]  # no "done" after an error
    