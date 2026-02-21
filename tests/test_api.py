"""API endpoint tests."""
import pytest
from unittest.mock import MagicMock

from backend.api.schemas import QueryRequest, QueryResponse


def test_health(client):
    """Health endpoint returns ok."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_query_endpoint(client, mock_assets, mock_chain):
    """Query endpoint returns answer when retrieval finds chunks."""
    # Make build_merged_chunks return some chunks by mocking index and bm25
    node_scores = [MagicMock(), MagicMock()]
    node_scores[0].node = MagicMock()
    node_scores[0].node.node_id = "n1"
    node_scores[1].node = MagicMock()
    node_scores[1].node.node_id = "n2"

    retriever = MagicMock()
    retriever.retrieve.return_value = node_scores
    mock_assets.index.as_retriever.return_value = retriever

    import numpy as np
    mock_assets.bm25.get_scores.return_value = np.array([0.5, 0.3])  # n1, n2

    r = client.post("/query", json={"question": "What is contract law?"})
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data
    assert data["answer"] == "Based on the documents, the answer is X."
    assert "sources" in data
    assert data["cache_hit"] is False


def test_query_cache_hit(client, mock_assets, mock_cache):
    """Query returns cached answer when cache hits."""
    mock_cache.check.return_value = "Cached answer here"

    r = client.post("/query", json={"question": "cached question?"})
    assert r.status_code == 200
    data = r.json()
    assert data["answer"] == "Cached answer here"
    assert data["cache_hit"] is True


def test_query_schema():
    """QueryRequest and QueryResponse validate correctly."""
    req = QueryRequest(question="test", doc_type=None)
    assert req.question == "test"
    assert req.doc_type is None

    resp = QueryResponse(answer="x", sources=["s1"], cache_hit=False)
    assert resp.answer == "x"
    assert resp.sources == ["s1"]
    assert resp.cache_hit is False
