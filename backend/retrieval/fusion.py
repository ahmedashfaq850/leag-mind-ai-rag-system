from backend.core.logging import get_logger

logger = get_logger(__name__)

def reciprocal_rank_fusion(vector_results, bm25_results, k: int = 60):
    scores: dict[str, float] = {}

    for rank, r in enumerate(vector_results):
        doc_id = r.node.node_id
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)

    for rank, r in enumerate(bm25_results):
        doc_id = r.get("id", str(rank))
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)

    merged_ids = sorted(scores, key=scores.get, reverse=True)
    logger.info(f"[fusion] merged={len(merged_ids)}")
    return merged_ids