from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    ENV: str = Field(default="development")

    OPENAI_API_KEY: str | None = None
    COHERE_API_KEY: str | None = None
    USE_COHERE_RERANK: bool = Field(default=True, description="Set False to use no-op reranker (avoids rate limits with trial keys)")
    REDIS_URL: str = Field(default="redis://localhost:6379")

    EMBED_PROVIDER: str = Field(default="openai")  
    EMBED_MODEL: str = Field(default="text-embedding-3-small")

    VECTOR_STORE: str = Field(default="faiss")

    CHUNK_SIZE: int = Field(default=512)
    CHUNK_OVERLAP: int = Field(default=51)

    TOP_K: int = Field(default=8)
    RERANK_TOP_K: int = Field(default=5)

    STORAGE_DIR: str = Field(default="./storage")
    DOCUMENTS_DIR: str = Field(default="./documents")

    LLM_MODEL: str = Field(default="gpt-4o-mini")
    LLM_TEMPERATURE: float = Field(default=0.0)

    EVAL_API_URL: str = Field(default="http://127.0.0.1:8000/query")
    EVAL_DATASET_PATH: str = Field(default="tests/golden_dataset.json")

    LOG_LEVEL: str = Field(default="INFO")

@lru_cache()
def get_settings() -> Settings:
    return Settings()