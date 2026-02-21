from backend.core.config import get_settings
from backend.core.logging import get_logger

from backend.retrieval.vector_search import vector_search
from backend.retrieval.bm25_search import bm25_search
from backend.retrieval.fusion import reciprocal_rank_fusion

logger = get_logger(__name__)

def build_merged_chunks(assets, query: str, top_k: int):
    s = get_settings()

    vec = vector_search(assets.index, query, top_k=top_k)
    bm = bm25_search(assets.bm25, assets.nodes_list, query, top_k=top_k)

    merged_ids = reciprocal_rank_fusion(vec, bm)

    merged_chunks = []
    for cid in merged_ids[:top_k]:
        if cid in assets.nodes_by_id:
            merged_chunks.append(assets.nodes_by_id[cid])

    # Note: vector_results have node ids that should match node_data ids
    logger.info(f"[retriever] merged_chunks={len(merged_chunks)}")
    return merged_chunks