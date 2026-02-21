from openai import OpenAI
from typing import List
from backend.core.config import get_settings
from backend.core.embeddings.base import BaseEmbedder

# Default dimensions for known OpenAI embedding models
_MODEL_DIMENSIONS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}


class OpenAIEmbedder(BaseEmbedder):

    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.EMBED_MODEL
        self.name = f"openai:{self.model}"
        self.dimension = _MODEL_DIMENSIONS.get(self.model, 1536)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding