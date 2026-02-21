from llama_index.core.node_parser import SentenceSplitter
from backend.core.logging import get_logger
from backend.core.exceptions import ChunkingError
from backend.core.config import get_settings

logger = get_logger(__name__)

def infer_doc_type(filename: str) -> str:
    f = filename.lower()
    if "contract" in f: return "contract"
    if "case" in f: return "case_file"
    return "other"

def chunk_documents(documents):
    s = get_settings()
    try:
        logger.info(f"[chunker] Chunking with chunk_size={s.CHUNK_SIZE}, overlap={s.CHUNK_OVERLAP}")
        splitter = SentenceSplitter(
            chunk_size=s.CHUNK_SIZE,
            chunk_overlap=s.CHUNK_OVERLAP
        )
        nodes = splitter.get_nodes_from_documents(documents)

        for node in nodes:
            file_name = node.metadata.get("file_name", "")
            node.metadata["doc_type"] = infer_doc_type(file_name)
            node.metadata["chunk_id"] = node.node_id

        logger.info(f"[chunker] Produced {len(nodes)} chunks (nodes)")
        return nodes
    except Exception as e:
        raise ChunkingError(f"Chunking failed: {e}") from e