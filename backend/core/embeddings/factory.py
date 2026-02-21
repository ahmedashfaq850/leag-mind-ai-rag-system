from backend.core.config import get_settings
from backend.core.embeddings.openai_embedder import OpenAIEmbedder
from backend.core.embeddings.base import BaseEmbedder


def get_llama_embed_model():
    """Return a LlamaIndex BaseEmbedding for loading/building indices (uses config .env)."""
    s = get_settings()
    if s.EMBED_PROVIDER == "openai":
        from llama_index.embeddings.openai import OpenAIEmbedding
        return OpenAIEmbedding(model=s.EMBED_MODEL, api_key=s.OPENAI_API_KEY)
    raise ValueError(f"Unsupported embed provider: {s.EMBED_PROVIDER}")


def get_embedder() -> BaseEmbedder:
    settings = get_settings()

    if settings.EMBED_PROVIDER == "openai":
        return OpenAIEmbedder()

    raise ValueError("Unsupported embedding provider")