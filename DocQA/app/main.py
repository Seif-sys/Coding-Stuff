from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from . import pipeline

app = FastAPI(title="DocQA", description="Ask questions about a text with an LLM.")


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    text: str = Field(min_length=1)
    k: int = Field(default=3, ge=1, le=10)  # how many chunks to give the LLM


class AskResponse(BaseModel):
    answer: str


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
