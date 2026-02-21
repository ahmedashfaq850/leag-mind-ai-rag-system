from llama_index.core import SimpleDirectoryReader
from backend.core.logging import get_logger
from backend.core.exceptions import DocumentLoadError

logger = get_logger(__name__)

def load_documents(directory: str):
    try:
        logger.info(f"[loader] Loading documents from: {directory}")
        reader = SimpleDirectoryReader(
            input_dir=directory,
            recursive=True,
            required_exts=[".pdf", ".docx", ".txt"]
        )
        docs = reader.load_data()
        logger.info(f"[loader] Loaded {len(docs)} documents")
        return docs
    except Exception as e:
        raise DocumentLoadError(f"Failed loading documents from {directory}: {e}") from e