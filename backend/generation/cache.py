import json
import numpy as np

from backend.core.config import get_settings
from backend.core.logging import get_logger

logger = get_logger(__name__)

CACHE_KEYS_LIST = "cache:keys"   # list of cache keys (bounded)


def get_cache():
    """Return SemanticCache if Redis available, else NoOpCache."""
    try:
        return SemanticCache()
    except Exception as e:
        logger.warning(f"[cache] Redis unavailable ({e}), using no-op cache")
        return NoOpCache()


class NoOpCache:
    """No-op cache when Redis is unavailable."""

    def check(self, query: str, threshold: float = 0.95):
        return None

    def save(self, query: str, answer: str, ttl_seconds: int = 3600):
        pass


def cosine_similarity(a, b):
    a = np.array(a, dtype="float32")
    b = np.array(b, dtype="float32")
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


class SemanticCache:
    def __init__(self, max_keys: int = 300):
        import redis
        from backend.core.embeddings.factory import get_embedder
        s = get_settings()
        self.r = redis.from_url(s.REDIS_URL)
        self.r.ping()  # verify connection
        self.embedder = get_embedder()
        self.max_keys = max_keys

    def _embed_query(self, text: str) -> list[float]:
        return self.embedder.embed_query(text)

    def check(self, query: str, threshold: float = 0.95):
        qv = self._embed_query(query)

        # Get recent keys only (bounded)
        keys = self.r.lrange(CACHE_KEYS_LIST, 0, self.max_keys - 1)
        if not keys:
            return None

        for k in keys:
            raw = self.r.get(k)
            if not raw:
                continue
            cached = json.loads(raw)
            sim = cosine_similarity(qv, cached["embedding"])
            if sim >= threshold:
                logger.info(f"[cache] HIT sim={sim:.3f}")
                return cached["answer"]

        logger.info("[cache] MISS")
        return None

    def save(self, query: str, answer: str, ttl_seconds: int = 3600):
        key = f"cache:{abs(hash(query))}"
        payload = {
            "embedding": self._embed_query(query),
            "answer": answer
        }
        self.r.setex(key, ttl_seconds, json.dumps(payload))

        # push into recent keys list and trim
        self.r.lpush(CACHE_KEYS_LIST, key)
        self.r.ltrim(CACHE_KEYS_LIST, 0, self.max_keys - 1)

        logger.info("[cache] SAVED")