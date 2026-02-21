from backend.core.logging import get_logger

logger = get_logger(__name__)

def vector_search(index, query: str, top_k: int = 20, filters=None):
    logger.info(f"[vector_search] top_k={top_k}")

    # LlamaIndex retriever (filters optional later)
    retriever = index.as_retriever(similarity_top_k=top_k)
    results = retriever.retrieve(query)

    logger.info(f"[vector_search] got={len(results)}")
    return results