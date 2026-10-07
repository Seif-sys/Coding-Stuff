import pytest

from app.rag import split_chunks, top_chunks


def test_split_chunks_overlap():
    chunks = split_chunks("abcdefghij", size=4, overlap=2)
    assert chunks[0] == "abcd"
    assert chunks[1] == "cdef"  # starts 2 characters later, shares 2 characters


def test_split_chunks_empty():
    assert split_chunks("   ") == []


def test_split_chunks_rejects_bad_params():
    with pytest.raises(ValueError):
        split_chunks("abc", size=2, overlap=2)


def test_top_chunks_finds_relevant_chunk():
    text = ("Bananas are yellow and grow in tropical regions. " * 3
            + "The Atlas rover uses six wheels and a nuclear battery. " * 3
            + "Pizza dough needs flour, water and yeast. " * 3)
    best = top_chunks(text, "How many wheels does the rover have?", k=1, size=150, overlap=30)[0]
    assert "wheels" in best


def test_top_chunks_empty_text():
    assert top_chunks("", "anything?") == []


def test_top_chunks_no_usable_words():
    # must not crash: falls back to the first chunks
    assert top_chunks("t", "q?", k=1) == ["t"]
