from typing import List, Dict
import re

def _tokenize(text: str) -> set:
    # very lightweight tokenization
    return set(re.findall(r"[A-Za-z0-9]+", text.lower()))

def validate_citations(answer: str, retrieved_chunks: List[Dict], sources: List[str]) -> dict:
    retrieved_docs = {c.get("doc") for c in retrieved_chunks if c.get("doc")}
    answer_tokens = _tokenize(answer)

    broken = [s for s in sources if s not in retrieved_docs]

    # Evidence check: for each cited doc, at least one chunk shares enough tokens with answer
    weak = []
    for s in sources:
        chunks = [c for c in retrieved_chunks if c.get("doc") == s]
        if not chunks:
            continue
        best_overlap = 0.0
        for c in chunks:
            t = _tokenize(c.get("text", ""))
            if not t:
                continue
            overlap = len(answer_tokens & t) / max(1, len(answer_tokens))
            best_overlap = max(best_overlap, overlap)
        if best_overlap < 0.15:  # heuristic threshold
            weak.append({"source": s, "best_overlap": round(best_overlap, 3)})

    return {
        "total_sources": len(sources),
        "retrieved_docs": sorted([d for d in retrieved_docs if d]),
        "broken_sources": broken,
        "weak_sources": weak,
        "passed": (len(broken) == 0 and len(weak) == 0)
    }