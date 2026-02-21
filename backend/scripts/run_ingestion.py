import os
from backend.core.config import get_settings
from backend.core.logging import setup_logging, get_logger

from backend.core.embeddings.factory import get_embedder
from backend.ingestion.loader import load_documents
from backend.ingestion.chunker import chunk_documents
from backend.ingestion.indexer import build_vector_index, build_bm25_index, write_manifest

logger = get_logger(__name__)

def main():
    s = get_settings()
    setup_logging(s.LOG_LEVEL)

    logger.info("=== PHASE 1: INGESTION START ===")

    documents_dir = s.DOCUMENTS_DIR
    storage_dir = s.STORAGE_DIR

    # 1) Load docs
    docs = load_documents(documents_dir)

    # 2) Chunk docs
    nodes = chunk_documents(docs)

    # 3) Embedder (provider-injected)
    embedder = get_embedder()
    logger.info(f"[embedder] Using: {embedder.name} (dim={embedder.dimension})")

    # 4) Build indexes
    build_vector_index(nodes, embedder, storage_dir=storage_dir)
    build_bm25_index(nodes, storage_dir=storage_dir)

    # 5) Manifest
    write_manifest(embedder_name=embedder.name, embed_dim=embedder.dimension, storage_dir=storage_dir)

    logger.info("=== PHASE 1: INGESTION DONE ===")
    logger.info(f"Storage ready at: {os.path.abspath(storage_dir)}")

if __name__ == "__main__":
    main()