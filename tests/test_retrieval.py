"""Retrieval logic unit tests."""
import pytest
from unittest.mock import MagicMock, patch
import numpy as np

from backend.retrieval.fusion import reciprocal_rank_fusion
from backend.retrieval.bm25_search import bm25_search


def test_reciprocal_rank_fusion():
    """RRF merges vector and BM25 results by score."""
    vec_results = [
        MagicMock(), MagicMock(), MagicMock(),
    ]
    vec_results[0].node = MagicMock()
    vec_results[0].node.node_id = "a"
    vec_results[1].node = MagicMock()
    vec_results[1].node.node_id = "b"
    vec_results[2].node = MagicMock()
    vec_results[2].node.node_id = "c"

    bm25_results = [
        {"id": "b", "text": "b"},
        {"id": "a", "text": "a"},
        {"id": "d", "text": "d"},
    ]

    merged = reciprocal_rank_fusion(vec_results, bm25_results, k=60)
    # Both lists have a, b. So a and b should rank high. c only in vec, d only in bm25.
    assert "a" in merged
    assert "b" in merged
    assert "c" in merged
    assert "d" in merged
    assert len(merged) == 4
    # a and b appear in both, so they should be first
    assert merged[0] in ("a", "b")
    assert merged[1] in ("a", "b")


def test_bm25_search():
    """BM25 search returns top-k nodes by score."""
    from rank_bm25 import BM25Okapi

    corpus = [
        ["contract", "law", "agreement"],
        ["liability", "limit"],
        ["contract", "breach"],
    ]
    bm25 = BM25Okapi(corpus)
    nodes = [
        {"id": "n1", "text": "contract law agreement", "metadata": {}},
        {"id": "n2", "text": "liability limit", "metadata": {}},
        {"id": "n3", "text": "contract breach", "metadata": {}},
    ]

    results = bm25_search(bm25, nodes, "contract", top_k=2)
    assert len(results) == 2
    ids = [r["id"] for r in results]
    assert "n1" in ids or "n3" in ids  # both contain "contract"


def test_build_merged_chunks(mock_assets):
    """build_merged_chunks returns chunks from assets.nodes_by_id."""
    from backend.retrieval.retriever import build_merged_chunks

    vec_results = [MagicMock()]
    vec_results[0].node = MagicMock()
    vec_results[0].node.node_id = "n1"

    retriever = MagicMock()
    retriever.retrieve.return_value = vec_results
    mock_assets.index.as_retriever.return_value = retriever

    mock_assets.bm25.get_scores.return_value = np.array([0.1, 0.2])

    with patch("backend.retrieval.retriever.vector_search") as mock_vs:
        with patch("backend.retrieval.retriever.bm25_search") as mock_bm:
            mock_vs.return_value = vec_results
            mock_bm.return_value = [{"id": "n2", "text": "x", "metadata": {}}]

            chunks = build_merged_chunks(mock_assets, "query", top_k=20)
            assert len(chunks) >= 1
            assert all("id" in c and "text" in c for c in chunks)
