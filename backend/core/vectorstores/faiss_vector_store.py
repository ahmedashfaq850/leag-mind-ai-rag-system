import faiss
import numpy as np
from typing import List
from backend.core.vectorstores.base import BaseVectorStore


class FAISSVectorStore(BaseVectorStore):

    def __init__(self, dimension: int):
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata = []

    def add(self, embeddings: List[List[float]], metadata: List[dict]):
        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)
        self.metadata.extend(metadata)

    def search(self, query_vector: List[float], top_k: int):
        vector = np.array([query_vector]).astype("float32")
        distances, indices = self.index.search(vector, top_k)
        results = []

        for idx in indices[0]:
            results.append(self.metadata[idx])

        return results