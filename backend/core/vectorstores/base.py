from abc import ABC, abstractmethod
from typing import List


class BaseVectorStore(ABC):

    @abstractmethod
    def add(self, embeddings: List[List[float]], metadata: List[dict]):
        pass

    @abstractmethod
    def search(self, query_vector: List[float], top_k: int):
        pass