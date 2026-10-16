from . import llm, rag
from .documents import Chunk, Document

PROMPT = """Answer the question using ONLY the context below.
If the context does not contain the answer, reply exactly: "Not in the document."

Context:
{context}

Question: {question}
Answer briefly."""


def _ask_llm(context_chunks: list[str], question: str) -> str:
    prompt = PROMPT.format(context="\n---\n".join(context_chunks), question=question)
    return llm.complete(prompt)  # looked up at call time, so tests can monkeypatch it


def answer(text: str, question: str, k: int = 3) -> str:
    return _ask_llm(rag.top_chunks(text, question, k=k), question)


def answer_docs(docs: list[Document], question: str, k: int = 3) -> tuple[str, list[tuple[Document, Chunk]]]:
    """Answer from the chunks of the given documents. Returns (answer, [(doc, chunk), ...])."""
    pool = [(d, c) for d in docs for c in d.chunks]
    top = [pool[i] for i in rag.best_indices([c.text for _, c in pool], question, k)]
    return _ask_llm([c.text for _, c in top], question), top