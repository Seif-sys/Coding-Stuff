from typing import Iterator

from . import llm, rag
from .documents import Chunk, Document

PROMPT = """Answer the question using ONLY the context below.
If the context does not contain the answer, reply exactly: "Not in the document."

Context:
{context}

Question: {question}
Answer briefly."""


def _prompt(context_chunks: list[str], question: str) -> str:
    return PROMPT.format(context="\n---\n".join(context_chunks), question=question)


def _retrieve(docs: list[Document], question: str, k: int) -> list[tuple[Document, Chunk]]:
    pool = [(d, c) for d in docs for c in d.chunks]
    return [pool[i] for i in rag.best_indices([c.text for _, c in pool], question, k)]


def answer(text: str, question: str, k: int = 3) -> str:
    return llm.complete(_prompt(rag.top_chunks(text, question, k=k), question))  # looked up at call time, so tests can monkeypatch it


def answer_docs(docs: list[Document], question: str, k: int = 3) -> tuple[str, list[tuple[Document, Chunk]]]:
    top = _retrieve(docs, question, k)
    return llm.complete(_prompt([c.text for _, c in top], question)), top


def stream_text(text: str, question: str, k: int = 3) -> Iterator[str]:
    return llm.stream(_prompt(rag.top_chunks(text, question, k=k), question))


def stream_docs(docs: list[Document], question: str, k: int = 3) -> tuple[Iterator[str], list[tuple[Document, Chunk]]]:
    top = _retrieve(docs, question, k)
    return llm.stream(_prompt([c.text for _, c in top], question)), top
