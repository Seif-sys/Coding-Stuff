from . import llm, rag

PROMPT = """Answer the question using ONLY the context below.
If the context does not contain the answer, reply exactly: "Not in the document."

Context:
{context}

Question: {question}
Answer briefly."""


def answer(text: str, question: str, k: int = 3) -> str:
    chunks = rag.top_chunks(text, question, k=k)
    prompt = PROMPT.format(context="\n---\n".join(chunks), question=question)
    return llm.complete(prompt)  # looked up at call time, so tests can monkeypatch it
