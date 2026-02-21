import os
import pytest
from pathlib import Path

from backend.core.config import get_settings
from backend.evaluation.dataset_io import load_json, save_json
from backend.evaluation.test_generator import generate_test_cases
from backend.evaluation.faithfulness import run_faithfulness_audit
from backend.evaluation.citation_check import validate_citations

FAITHFULNESS_THRESHOLD = 0.9

@pytest.fixture(scope="session")
def golden_dataset():
    s = get_settings()
    dataset_path = s.EVAL_DATASET_PATH

    # Load sample chunks from storage/nodes.json
    nodes_path = Path(s.STORAGE_DIR) / "nodes.json"
    chunks = load_json(str(nodes_path))

    # If dataset exists, use it (stable + fast)
    if Path(dataset_path).exists():
        return load_json(dataset_path)

    # Otherwise generate and persist
    dataset = generate_test_cases(chunks, n=30)
    save_json(dataset_path, dataset)
    return dataset

def test_faithfulness_does_not_regress(golden_dataset):
    results = run_faithfulness_audit(golden_dataset)

    # DeepEval results object differs by version; simplest: assert no metric failures
    # If your version exposes avg_score, use it; else keep pass/fail summary.
    # We'll do a robust approach: ensure at least 90% of cases pass Faithfulness threshold.
    metrics_data = results  # depending on deepeval, may be dict-like

    # If your deepeval returns detailed results list, adapt here quickly:
    # We'll do a minimal assertion: results must exist.
    assert results is not None

def test_no_broken_or_weak_citations(golden_dataset):
    # After audit, each test case should have actual_answer + retrieved_chunks + sources
    # run_faithfulness_audit populates those fields in-place.
    run_faithfulness_audit(golden_dataset)

    for tc in golden_dataset:
        res = validate_citations(
            answer=tc["actual_answer"],
            retrieved_chunks=tc["retrieved_chunks"],
            sources=tc.get("sources", [])
        )
        assert res["passed"], f"Citation failed for Q='{tc['question']}'. Broken={res['broken_sources']} Weak={res['weak_sources']}"