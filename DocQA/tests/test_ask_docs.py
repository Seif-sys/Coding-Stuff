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


def make_doc(name, chunks):
    return store.add(name, [Chunk(text, page) for text, page in chunks])


def test_ask_docs_returns_answer_and_sources(monkeypatch):
    seen = {}

    def fake_complete(prompt, max_tokens=500):
        seen["prompt"] = prompt
        return "Bremen"

    monkeypatch.setattr("app.llm.complete", fake_complete)
    a = make_doc("a.pdf", [("The capital of Germany is Berlin.", 1), ("Bananas are yellow.", 2)])
    b = make_doc("b.pdf", [("The harbour city Bremen lies on the Weser.", 7)])
    r = client.post("/ask", json={"question": "Which city lies on the Weser?", "doc_ids": [a.id, b.id], "k": 1})
    assert r.status_code == 200
    assert r.json() == {
        "answer": "Bremen",
        "sources": [{"doc_id": b.id, "doc": "b.pdf", "page": 7,
                     "text": "The harbour city Bremen lies on the Weser."}],
    }
    assert "Weser" in seen["prompt"]  # retrieved context really reached the prompt


def test_ask_only_searches_selected_docs(monkeypatch):
    monkeypatch.setattr("app.llm.complete", lambda p, max_tokens=500: "x")
    a = make_doc("a.pdf", [("alpha beta gamma", 1)])
    make_doc("b.pdf", [("alpha beta gamma", 1)])
    r = client.post("/ask", json={"question": "alpha?", "doc_ids": [a.id]})
    assert {s["doc_id"] for s in r.json()["sources"]} == {a.id}


def test_ask_unknown_doc_is_404():
    r = client.post("/ask", json={"question": "q?", "doc_ids": ["nope"]})
    assert r.status_code == 404


def test_ask_requires_exactly_one_input():
    assert client.post("/ask", json={"question": "q?"}).status_code == 422
    both = {"question": "q?", "text": "t", "doc_ids": ["x"]}
    assert client.post("/ask", json=both).status_code == 422


def test_ask_docs_llm_failure_is_502(monkeypatch):
    def boom(prompt, max_tokens=500):
        raise RuntimeError("no key")

    monkeypatch.setattr("app.llm.complete", boom)
    d = make_doc("a.pdf", [("some text", 1)])
    r = client.post("/ask", json={"question": "q?", "doc_ids": [d.id]})
    assert r.status_code == 502
    