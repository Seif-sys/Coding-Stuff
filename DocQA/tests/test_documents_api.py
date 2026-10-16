import pytest
from fastapi.testclient import TestClient

from app.documents import store
from app.main import app

client = TestClient(app)
FAKE_PDF = b"%PDF-1.4 fake"


@pytest.fixture(autouse=True)
def clean_store():
    store.clear()
    yield
    store.clear()


def upload(monkeypatch, pages=("Page one text.", "Page two text."), name="a.pdf", data=FAKE_PDF):
    monkeypatch.setattr("app.main.pdf.extract_pages", lambda d: list(pages))
    return client.post("/documents", files={"file": (name, data, "application/pdf")})


def test_upload_ok(monkeypatch):
    r = upload(monkeypatch)
    assert r.status_code == 201
    body = r.json()
    assert body["filename"] == "a.pdf"
    assert body["n_chunks"] == 2  # one short chunk per page


def test_upload_rejects_non_pdf(monkeypatch):
    r = upload(monkeypatch, name="a.txt", data=b"hello")
    assert r.status_code == 415


def test_upload_rejects_empty_text(monkeypatch):
    r = upload(monkeypatch, pages=("", "  "))
    assert r.status_code == 422


def test_upload_rejects_too_large(monkeypatch):
    monkeypatch.setattr("app.main.MAX_BYTES", 10)
    r = upload(monkeypatch)
    assert r.status_code == 413

def test_list_and_delete(monkeypatch):
    doc_id = upload(monkeypatch).json()["doc_id"]
    assert [d["doc_id"] for d in client.get("/documents").json()] == [doc_id]
    assert client.delete(f"/documents/{doc_id}").status_code == 204
    assert client.get("/documents").json() == []
    assert client.delete(f"/documents/{doc_id}").status_code == 404
    