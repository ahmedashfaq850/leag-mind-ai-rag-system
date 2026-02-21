"""Pytest fixtures for law firm RAG system tests."""
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from backend.api.main import create_app
from backend.api.deps import get_assets, get_chain, get_cache, get_reranker


@pytest.fixture
def mock_assets():
    """Minimal RetrievalAssets for testing retrieval logic."""
    nodes = [
        {"id": "n1", "text": "Contract law governs agreements.", "metadata": {"file_name": "contracts.pdf"}},
        {"id": "n2", "text": "Liability limits apply.", "metadata": {"file_name": "liability.docx"}},
    ]
    return MagicMock(
        nodes_list=nodes,
        nodes_by_id={n["id"]: n for n in nodes},
        index=MagicMock(),
        bm25=MagicMock(),
        manifest={"embedding_provider": "openai"},
    )


@pytest.fixture
def mock_chain():
    """Chain that returns structured RAGOutput."""
    chain = MagicMock()
    output = MagicMock()
    output.answer = "Based on the documents, the answer is X."
    output.sources_used = ["contracts.pdf"]
    chain.invoke.return_value = output
    return chain


@pytest.fixture
def mock_cache():
    """Cache that always misses."""
    cache = MagicMock()
    cache.check.return_value = None
    return cache


@pytest.fixture
def mock_reranker():
    """Reranker that returns chunks as-is."""
    reranker = MagicMock()
    reranker.rerank.side_effect = lambda q, chunks, top_n=5, **kw: chunks[:top_n]
    return reranker


@pytest.fixture
def client(mock_assets, mock_chain, mock_cache, mock_reranker):
    """Test client with mocked dependencies."""
    app = create_app()

    def override_get_assets():
        return mock_assets

    def override_get_chain():
        return mock_chain

    def override_get_cache():
        return mock_cache

    def override_get_reranker():
        return mock_reranker

    app.dependency_overrides = {
        get_assets: override_get_assets,
        get_chain: override_get_chain,
        get_cache: override_get_cache,
        get_reranker: override_get_reranker,
    }
    return TestClient(app)
