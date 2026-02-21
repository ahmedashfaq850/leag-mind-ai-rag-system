from backend.core.config import get_settings
from backend.core.logging import get_logger

logger = get_logger(__name__)


def get_reranker():
    """Return CohereReranker only if COHERE_API_KEY set and USE_COHERE_RERANK=True, else NoOpReranker."""
    s = get_settings()
    if s.COHERE_API_KEY and s.USE_COHERE_RERANK:
        return CohereReranker()
    if s.COHERE_API_KEY and not s.USE_COHERE_RERANK:
        logger.info("[reranker] USE_COHERE_RERANK=False, using pass-through reranker (trial key / rate limit bypass)")
    else:
        logger.warning("[reranker] COHERE_API_KEY not set, using pass-through reranker")
    return NoOpReranker()


class NoOpReranker:
    """Pass-through reranker when Cohere is unavailable."""

    def rerank(self, query: str, chunks: list[dict], top_n: int = 5, **kwargs):
        if not chunks:
            return []
        logger.info(f"[reranker] no-op, returning top_n={top_n} of {len(chunks)}")
        return chunks[:top_n]


class CohereReranker:
    def __init__(self):
        import cohere
        s = get_settings()
        self.client = cohere.Client(s.COHERE_API_KEY)

    def rerank(self, query: str, chunks: list[dict], top_n: int = 5, model: str = "rerank-english-v3.0"):
        if not chunks:
            return []
        logger.info(f"[reranker] reranking {len(chunks)} -> top_n={top_n}")
        documents = [c["text"] for c in chunks]
        response = self.client.rerank(
            query=query,
            documents=documents,
            top_n=min(top_n, len(documents)),
            model=model
        )
        reranked = [chunks[r.index] for r in response.results]
        logger.info(f"[reranker] done, returned={len(reranked)}")
        return reranked