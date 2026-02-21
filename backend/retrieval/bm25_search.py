from backend.core.logging import get_logger

logger = get_logger(__name__)

def bm25_search(bm25, nodes_list: list[dict], query: str, top_k: int = 20):
    logger.info(f"[bm25_search] top_k={top_k}")

    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)

    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    results = [nodes_list[i] for i in top_indices]

    logger.info(f"[bm25_search] got={len(results)}")
    return results