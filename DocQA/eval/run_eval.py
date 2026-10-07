""" 
Measures how good the pipeline is: accuracy on eval/cases.json.

Usage (from the project root):
  python -m eval.run_eval --offline          # no API key: retrieval-only baseline
  python -m eval.run_eval                    # real LLM, needs ANTHROPIC_API_KEY
  python -m eval.run_eval --k 1 2 3 5        # compare several values of k
  """


import argparse
import json
from pathlib import Path

from app import pipeline, rag

HERE = Path(__file__).parent


def offline_answer(text: str, question: str, k: int) -> str:
    """Baseline without an LLM: just return the retrieved chunks.
    The "Not in the document" case can never pass here; that is the point of a baseline."""
    return " ".join(rag.top_chunks(text, question, k=k))


def run(k: int, offline: bool) -> tuple[int, int, list[dict]]:
    text = (HERE / "document.txt").read_text()
    cases = json.loads((HERE / "cases.json").read_text())
    fn = offline_answer if offline else pipeline.answer
    hits, misses = 0, []
    for c in cases:
        ans = fn(text, c["question"], k)
        if c["expected"].lower() in ans.lower():
            hits += 1
        else:
            misses.append({"question": c["question"], "expected": c["expected"], "got": ans[:120]})
    return hits, len(cases), misses


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, nargs="+", default=[3])
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()
    for k in args.k:
        hits, n, misses = run(k, args.offline)
        print(f"k={k}: {hits}/{n} correct ({100 * hits / n:.0f}%)")
        for m in misses:
            print(f"   MISS  {m['question']!r} expected {m['expected']!r}, got {m['got']!r}")
