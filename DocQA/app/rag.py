from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def split_chunks(text: str, size: int = 400, overlap: int = 80) -> list[str]:
    """Cut text into chunks of ~`size` characters; neighbours share `overlap` characters
    so a sentence at a boundary is not lost."""
    if size <= overlap:
        raise ValueError("size must be larger than overlap")
    text = text.strip()
    if not text:
        return []
    step = size - overlap
    return [text[i:i + size] for i in range(0, len(text), step)]


def best_indices(texts: list[str], question: str, k: int = 3) -> list[int]:
    """Indices of the k texts most similar to the question, best first."""
    if not texts:
        return []
    try:
        vec = TfidfVectorizer().fit(texts + [question])
    except ValueError:  # no usable words at all (e.g. only stop words/punctuation)
        return list(range(min(k, len(texts))))
    scores = cosine_similarity(vec.transform([question]), vec.transform(texts))[0]
    return [int(i) for i in scores.argsort()[::-1][:k]]


def top_chunks(text: str, question: str, k: int = 3, size: int = 400, overlap: int = 80) -> list[str]:
    """Return the k chunks most similar to the question, best first."""
    chunks = split_chunks(text, size, overlap)
    return [chunks[i] for i in best_indices(chunks, question, k)]
