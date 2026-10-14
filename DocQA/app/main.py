from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from . import pdf, pipeline, rag
from .documents import Chunk, store

MAX_BYTES = 10 * 1024 * 1024  # 10 MB

app = FastAPI(title="DocQA", description="Ask questions about a text with an LLM.")


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    text: str = Field(min_length=1)
    k: int = Field(default=3, ge=1, le=10)  # how many chunks to give the LLM


class AskResponse(BaseModel):
    answer: str


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    n_chunks: int


@app.get("/health")
def health():
    """Used by Docker/monitoring to check the service is alive."""
    return {"ok": True}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    try:
        return AskResponse(answer=pipeline.answer(req.text, req.question, req.k))
    except Exception as exc:  # e.g. Ollama not running, model missing
        raise HTTPException(status_code=502, detail=f"LLM call failed: {exc}")


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