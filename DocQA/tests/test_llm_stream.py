import json

from app.llm import groq, ollama


class FakeStream:
    def __init__(self, lines, status_code=200):
        self.lines = lines
        self.status_code = status_code

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def iter_lines(self):
        return iter(self.lines)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_ollama_stream_yields_pieces(monkeypatch):
    lines = [
        json.dumps({"message": {"content": "Bre"}, "done": False}),
        json.dumps({"message": {"content": "men"}, "done": False}),
        json.dumps({"message": {"content": ""}, "done": True}),
    ]
    monkeypatch.setattr(ollama.httpx, "stream", lambda method, url, **kw: FakeStream(lines))
    assert "".join(ollama.stream("Where?")) == "Bremen"


def test_groq_stream_yields_pieces(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test")
    lines = [
        "data: " + json.dumps({"choices": [{"delta": {"content": "Bre"}}]}),
        "",
        "data: " + json.dumps({"choices": [{"delta": {"content": "men"}}]}),
        "",
        "data: [DONE]",
    ]
    monkeypatch.setattr(groq.httpx, "stream", lambda method, url, **kw: FakeStream(lines))
    assert "".join(groq.stream("Where?")) == "Bremen"
    