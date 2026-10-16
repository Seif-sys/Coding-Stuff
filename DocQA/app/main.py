import json

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, model_validator

from . import pdf, pipeline, rag
from .documents import Chunk, Document, store

MAX_BYTES = 10 * 1024 * 1024  # 10 MB

app = FastAPI(title="DocQA", description="Ask questions about a text with an LLM.")


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    text: str | None = Field(default=None, min_length=1)         # old mode: raw text
    doc_ids: list[str] | None = Field(default=None, min_length=1)  # new mode: uploaded documents
    k: int = Field(default=3, ge=1, le=10)  # how many chunks to give the LLM

    @model_validator(mode="after")
    def exactly_one_input(self):
        if (self.text is None) == (self.doc_ids is None):
            raise ValueError("Provide either 'text' or 'doc_ids'.")
        return self


class Source(BaseModel):
    doc_id: str
    doc: str
    page: int
    text: str


class AskResponse(BaseModel):
    answer: str
    sources: list[Source] | None = None  # only set in doc_ids mode


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    n_chunks: int


def _resolve_docs(doc_ids: list[str]) -> list[Document]:
    docs = []
    for doc_id in dict.fromkeys(doc_ids):  # de-duplicate, keep order
        doc = store.get(doc_id)
        if doc is None:
            raise HTTPException(status_code=404, detail=f"Document not found: {doc_id}")
        docs.append(doc)
    return docs


def _sources(top: list[tuple[Document, Chunk]]) -> list[Source]:
    return [Source(doc_id=d.id, doc=d.filename, page=c.page, text=c.text) for d, c in top]


def _sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.get("/health")
def health():
    """Used by Docker/monitoring to check the service is alive."""
    return {"ok": True}


@app.post("/ask", response_model=AskResponse, response_model_exclude_none=True)
def ask(req: AskRequest):
    if req.doc_ids is None:
        try:
            return AskResponse(answer=pipeline.answer(req.text, req.question, req.k))
        except Exception as exc:  # e.g. Ollama not running, model missing
            raise HTTPException(status_code=502, detail=f"LLM call failed: {exc}")

    docs = _resolve_docs(req.doc_ids)
    try:
        answer, top = pipeline.answer_docs(docs, req.question, req.k)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {exc}")
    return AskResponse(answer=answer, sources=_sources(top))


@app.post("/ask/stream")
def ask_stream(req: AskRequest):
    docs = _resolve_docs(req.doc_ids) if req.doc_ids is not None else None  # 404 before streaming starts

    def events():
        try:
            if docs is None:
                tokens = pipeline.stream_text(req.text, req.question, req.k)
            else:
                tokens, top = pipeline.stream_docs(docs, req.question, req.k)
                yield _sse("sources", [s.model_dump() for s in _sources(top)])
            for piece in tokens:
                yield _sse("token", piece)
        except Exception as exc:
            yield _sse("error", f"LLM call failed: {exc}")
            return
        yield _sse("done", {})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/documents", response_model=DocumentInfo, status_code=201)
async def upload_document(file: UploadFile = File(...)):
    name = file.filename or "document.pdf"
    data = await file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB).")
    if not name.lower().endswith(".pdf") or not data.startswith(b"%PDF"):
        raise HTTPException(status_code=415, detail="Only PDF files are supported.")
    try:
        pages = pdf.extract_pages(data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    chunks = [
        Chunk(text=c, page=page_no)
        for page_no, page_text in enumerate(pages, start=1)
        for c in rag.split_chunks(page_text)
    ]
    if not chunks:
        raise HTTPException(status_code=422, detail="No extractable text (scanned PDF?).")
    doc = store.add(name, chunks)
    return DocumentInfo(doc_id=doc.id, filename=doc.filename, n_chunks=len(doc.chunks))


@app.get("/documents", response_model=list[DocumentInfo])
def list_documents():
    return [DocumentInfo(doc_id=d.id, filename=d.filename, n_chunks=len(d.chunks)) for d in store.list()]


@app.delete("/documents/{doc_id}", status_code=204)
def delete_document(doc_id: str):
    if not store.delete(doc_id):
        raise HTTPException(status_code=404, detail="Document not found.")
    