import json
import random
from typing import List, Dict

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from backend.core.config import get_settings
from backend.core.logging import get_logger

logger = get_logger(__name__)

PROMPT = """
You are a senior litigation attorney.
Given the legal text below, generate {n_questions} difficult questions a junior associate might ask.

Rules:
- Questions MUST be answerable from the text provided.
- Include multi-part questions when possible (but still answerable from this text).
- Avoid vague questions.
- Provide a short expected answer (1–3 sentences max).
- Output MUST be strict JSON only (no markdown, no commentary).

Return JSON array of objects:
[
  {{
    "question": "...",
    "expected_answer": "..."
  }}
]

Legal text:
{text}
""".strip()

def _safe_json_parse(text: str):
    """
    Handles cases where model returns extra text.
    We try to extract the first JSON array.
    """
    text = text.strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Could not find JSON array in model output: {text[:200]}")
    return json.loads(text[start:end+1])

def generate_test_cases(document_chunks: List[Dict], n: int = 50, chunks_sample: int = 12, per_chunk: int = 5):
    s = get_settings()

    llm = ChatOpenAI(
        model=getattr(s, "LLM_MODEL", "gpt-4o-mini"),
        temperature=0.7,
    )

    prompt = ChatPromptTemplate.from_messages([("human", PROMPT)])

    # sample diverse chunks
    sampled = random.sample(document_chunks, k=min(chunks_sample, len(document_chunks)))
    all_cases = []
    seen_q = set()

    for chunk in sampled:
        text = chunk.get("text", "")
        if not text or len(text) < 200:
            continue

        msg = prompt.format_messages(text=text, n_questions=per_chunk)
        resp = llm.invoke(msg)

        try:
            cases = _safe_json_parse(resp.content)
        except Exception as e:
            logger.warning(f"[test_generator] JSON parse failed: {e}")
            continue

        for c in cases:
            q = (c.get("question") or "").strip()
            a = (c.get("expected_answer") or "").strip()
            if not q or not a:
                continue
            if q.lower() in seen_q:
                continue

            seen_q.add(q.lower())
            all_cases.append({
                "question": q,
                "expected_answer": a,
                # keep traceability
                "seed_source": chunk.get("metadata", {}).get("file_name", "unknown"),
                "seed_chunk_id": chunk.get("id", "unknown")
            })

        if len(all_cases) >= n:
            break

    logger.info(f"[test_generator] Generated {len(all_cases)} test cases")
    return all_cases[:n]