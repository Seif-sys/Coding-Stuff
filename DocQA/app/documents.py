import uuid
from dataclasses import dataclass
from typing import Optional


@dataclass
class Chunk:
    text: str
    page: int


@dataclass
class Document:
    id: str
    filename: str
    chunks: list[Chunk]


class DocumentStore:
    """In-memory store. Swap this class for a persistent one later; callers stay unchanged."""

    def __init__(self):
        self._docs: dict[str, Document] = {}

    def add(self, filename: str, chunks: list[Chunk]) -> Document:
        doc = Document(id=uuid.uuid4().hex[:12], filename=filename, chunks=chunks)
        self._docs[doc.id] = doc
        return doc

    def get(self, doc_id: str) -> Optional[Document]:
        return self._docs.get(doc_id)

    def list(self) -> list[Document]:
        return list(self._docs.values())

    def delete(self, doc_id: str) -> bool:
        return self._docs.pop(doc_id, None) is not None

    def clear(self) -> None:
        self._docs.clear()


store = DocumentStore()
