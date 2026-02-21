import os
import json
import pickle
from dataclasses import dataclass

from llama_index.core import StorageContext, load_index_from_storage
from llama_index.vector_stores.faiss import FaissVectorStore

from backend.core.config import get_settings
from backend.core.embeddings.factory import get_llama_embed_model
from backend.core.constants import MANIFEST_FILE, BM25_FILE, NODES_FILE
from backend.core.logging import get_logger
from backend.core.exceptions import ConfigError

logger = get_logger(__name__)

@dataclass
class RetrievalAssets:
    index: object                # llamaindex VectorStoreIndex loaded from storage
    bm25: object                 # BM25Okapi
    nodes_list: list[dict]       # list of {id,text,metadata}
    nodes_by_id: dict[str, dict] # id -> node dict
    manifest: dict

def load_manifest(storage_dir: str) -> dict:
    path = os.path.join(storage_dir, MANIFEST_FILE)
    with open(path, "r") as f:
        return json.load(f)

def validate_manifest(manifest: dict) -> None:
    """Fail fast if runtime config doesn't match index build config."""
    s = get_settings()

    if manifest.get("embedding_provider") != s.EMBED_PROVIDER:
        raise ConfigError(
            f"Manifest mismatch: EMBED_PROVIDER={s.EMBED_PROVIDER} but index built with {manifest.get('embedding_provider')}"
        )

    if manifest.get("embedding_model") != s.EMBED_MODEL:
        raise ConfigError(
            f"Manifest mismatch: EMBED_MODEL={s.EMBED_MODEL} but index built with {manifest.get('embedding_model')}. Rebuild index."
        )

    if int(manifest.get("chunk_size", -1)) != int(s.CHUNK_SIZE):
        logger.warning(
            f"[retrieval.assets] chunk_size differs (runtime={s.CHUNK_SIZE}, manifest={manifest.get('chunk_size')}). Not fatal, but consider rebuild."
        )

def load_vector_index(storage_dir: str):
    logger.info("[retrieval.assets] Loading vector index from storage via LlamaIndex")

    # FAISS vector store persisted by LlamaIndex
    vector_store = FaissVectorStore.from_persist_dir(storage_dir)
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        persist_dir=storage_dir
    )
    embed_model = get_llama_embed_model()
    return load_index_from_storage(storage_context, embed_model=embed_model)

def load_retrieval_assets() -> RetrievalAssets:
    s = get_settings()
    storage_dir = s.STORAGE_DIR

    logger.info(f"[retrieval.assets] Loading assets from: {storage_dir}")

    manifest = load_manifest(storage_dir)
    validate_manifest(manifest)

    # nodes.json
    with open(os.path.join(storage_dir, NODES_FILE), "r") as f:
        nodes_list = json.load(f)
    nodes_by_id = {n["id"]: n for n in nodes_list}

    # bm25.pkl
    with open(os.path.join(storage_dir, BM25_FILE), "rb") as f:
        bm25 = pickle.load(f)

    # vector index
    index = load_vector_index(storage_dir)

    logger.info(
        f"[retrieval.assets] Loaded nodes={len(nodes_list)} | bm25_corpus={getattr(bm25,'corpus_size','?')}"
    )
    return RetrievalAssets(
        index=index,
        bm25=bm25,
        nodes_list=nodes_list,
        nodes_by_id=nodes_by_id,
        manifest=manifest
    )