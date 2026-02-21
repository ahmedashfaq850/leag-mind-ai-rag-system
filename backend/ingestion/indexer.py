import os, json, pickle
import faiss
from rank_bm25 import BM25Okapi

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.faiss import FaissVectorStore

from backend.core.logging import get_logger
from backend.core.exceptions import IndexBuildError
from backend.core.constants import MANIFEST_FILE, BM25_FILE, NODES_FILE
from backend.core.embeddings.factory import get_llama_embed_model

logger = get_logger(__name__)

def ensure_storage_dir(storage_dir: str) -> None:
    os.makedirs(storage_dir, exist_ok=True)

def build_vector_index(nodes, embed_model, storage_dir: str):
    try:
        ensure_storage_dir(storage_dir)

        # Dimension MUST come from embedder, not hardcoded
        dimension = embed_model.dimension
        logger.info(f"[indexer] Building FAISS index (dim={dimension})")

        faiss_index = faiss.IndexFlatL2(dimension)
        vector_store = FaissVectorStore(faiss_index=faiss_index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        llama_embed_model = get_llama_embed_model()
        index = VectorStoreIndex(
            nodes,
            storage_context=storage_context,
            embed_model=llama_embed_model,
        )

        index.storage_context.persist(persist_dir=storage_dir)
        logger.info(f"[indexer] FAISS index persisted to: {storage_dir}")
        return index

    except Exception as e:
        raise IndexBuildError(f"Vector index build failed: {e}") from e

def build_bm25_index(nodes, storage_dir: str):
    try:
        ensure_storage_dir(storage_dir)

        logger.info("[indexer] Building BM25 index")
        tokenized = [node.get_content().split() for node in nodes]
        bm25 = BM25Okapi(tokenized)

        node_data = [
            {"id": n.node_id, "text": n.get_content(), "metadata": n.metadata}
            for n in nodes
        ]

        with open(os.path.join(storage_dir, BM25_FILE), "wb") as f:
            pickle.dump(bm25, f)

        with open(os.path.join(storage_dir, NODES_FILE), "w") as f:
            json.dump(node_data, f)

        logger.info(f"[indexer] BM25 + nodes persisted to: {storage_dir}")
        return bm25

    except Exception as e:
        raise IndexBuildError(f"BM25 index build failed: {e}") from e

def write_manifest(embedder_name: str, embed_dim: int, storage_dir: str):
    s = get_settings()
    manifest = {
        "embedding_provider": s.EMBED_PROVIDER,
        "embedding_model": s.EMBED_MODEL,
        "embedding_name": embedder_name,
        "embedding_dimension": embed_dim,
        "chunk_size": s.CHUNK_SIZE,
        "chunk_overlap": s.CHUNK_OVERLAP,
        "vector_store": s.VECTOR_STORE,
    }
    path = os.path.join(storage_dir, MANIFEST_FILE)
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)
    logger.info(f"[indexer] Manifest written: {path}")
    return manifest