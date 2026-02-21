from backend.core.config import get_settings
from backend.core.vectorstores.faiss_vector_store import FAISSVectorStore


def get_vector_store(dimension: int):
    settings = get_settings()

    if settings.VECTOR_STORE == "faiss":
        return FAISSVectorStore(dimension)

    raise ValueError("Unsupported vector store")