from functools import lru_cache

from backend.retrieval.assets import load_retrieval_assets, RetrievalAssets
from backend.retrieval.reranker import get_reranker as _get_reranker
from backend.generation.cache import get_cache as _get_cache
from backend.generation.chain import build_rag_chain

@lru_cache()
def get_assets() -> RetrievalAssets:
    return load_retrieval_assets()

@lru_cache()
def get_reranker():
    return _get_reranker()

@lru_cache()
def get_cache():
    return _get_cache()

@lru_cache()
def get_chain():
    return build_rag_chain()