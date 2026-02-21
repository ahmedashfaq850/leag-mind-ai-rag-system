from typing import List, Dict
import requests

from deepeval import evaluate
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric, ContextualPrecisionMetric
from deepeval.test_case import LLMTestCase

from backend.core.config import get_settings
from backend.core.logging import get_logger

logger = get_logger(__name__)

def run_faithfulness_audit(test_cases: List[Dict]) -> dict:
    s = get_settings()
    api_url = s.EVAL_API_URL

    metrics = [
        FaithfulnessMetric(threshold=0.9),
        AnswerRelevancyMetric(threshold=0.8),
        ContextualPrecisionMetric(threshold=0.7),
    ]

    deepeval_cases = []

    for tc in test_cases:
        q = tc["question"]

        resp = requests.post(api_url, json={"question": q, "debug": True}, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        actual = data["answer"]
        retrieved = (data.get("debug", {}) or {}).get("retrieved_chunks", [])
        retrieval_context = [c["text"] for c in retrieved]

        # store for downstream checks
        tc["actual_answer"] = actual
        tc["retrieved_chunks"] = retrieved
        tc["sources"] = data.get("sources", [])

        deepeval_cases.append(
            LLMTestCase(
                input=q,
                actual_output=actual,
                expected_output=tc["expected_answer"],
                retrieval_context=retrieval_context
            )
        )

    logger.info(f"[faithfulness] Running DeepEval on {len(deepeval_cases)} cases")
    results = evaluate(deepeval_cases, metrics)
    return results