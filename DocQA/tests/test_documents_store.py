from app.documents import Chunk, DocumentStore


def test_add_get_delete():
    s = DocumentStore()
    doc = s.add("a.pdf", [Chunk("hello", 1)])
    assert s.get(doc.id).filename == "a.pdf"
    assert [d.id for d in s.list()] == [doc.id]
    assert s.delete(doc.id) is True
    assert s.get(doc.id) is None
    assert s.delete(doc.id) is False
    