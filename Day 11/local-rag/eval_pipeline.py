"""Runs five DeepEval RAG metrics over pipeline_outputs_<label>.json and writes eval_results_<label>.json.

    uv run python eval_pipeline.py local
    uv run python eval_pipeline.py cloud

Needs JUDGE_BASE_URL (your Foundry URL ending in /openai/v1/) and AZURE_OPENAI_API_KEY in the shell.
Judge gpt-5.4-mini; JUDGE_MODEL and EVAL_CONCURRENCY override the defaults.
"""

import json
import os
import sys

# The whole class shares one judge deployment (250 requests per minute): wait and retry on 429
# instead of recording an error. DeepEval reads these when it is imported.
os.environ.setdefault("DEEPEVAL_RETRY_MAX_ATTEMPTS", "6")
os.environ.setdefault("DEEPEVAL_RETRY_CAP_SECONDS", "30")
os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "1")

from deepeval import evaluate  # noqa: E402
from deepeval.evaluate import AsyncConfig, DisplayConfig, ErrorConfig
from deepeval.metrics import (
    AnswerRelevancyMetric, ContextualPrecisionMetric, ContextualRecallMetric,
    ContextualRelevancyMetric, FaithfulnessMetric,
)
from deepeval.models import OpenAIModel
from deepeval.test_case import LLMTestCase

JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "gpt-5.4-mini")


def make_judge():
    # gpt-4.1 models reject reasoning_effort; for gpt-5.x DeepEval already leaves out temperature
    extra = {} if JUDGE_MODEL.startswith("gpt-4") else {"reasoning_effort": "low"}
    return OpenAIModel(
        model=JUDGE_MODEL,
        base_url=os.environ["JUDGE_BASE_URL"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        generation_kwargs=extra,
    )


def main(label: str):
    with open(f"pipeline_outputs_{label}.json", encoding="utf-8") as f:
        rows = json.load(f)
    test_cases = [
        LLMTestCase(name=r["id"], input=r["question"], actual_output=r["actual_answer"],
                    expected_output=r["expected_answer"], retrieval_context=r["retrieved_context"])
        for r in rows
    ]
    judge = make_judge()
    # By default Faithfulness only fails claims that contradict the context; a claim the context
    # never mentions passes. The flag counts those against the score too.
    metrics = [FaithfulnessMetric(threshold=0.7, model=judge, penalize_ambiguous_claims=True)] + [
        m(threshold=0.7, model=judge) for m in (
            AnswerRelevancyMetric, ContextualRelevancyMetric, ContextualRecallMetric, ContextualPrecisionMetric)]
    result = evaluate(test_cases, metrics,
                      async_config=AsyncConfig(max_concurrent=int(os.environ.get("EVAL_CONCURRENCY", "2"))),
                      error_config=ErrorConfig(ignore_errors=True),
                      display_config=DisplayConfig(print_results=False))
    by_id = {r["id"]: r for r in rows}
    out = [{
        "id": tr.name,
        "question": by_id[tr.name]["question"],
        "model": by_id[tr.name]["model"],
        "generation_time_ms": by_id[tr.name]["generation_time_ms"],
        "judge": judge.get_model_name(),
        "metrics": {m.name: {"score": m.score, "success": m.success, "reason": m.reason, "error": m.error}
                    for m in tr.metrics_data or []},
    } for tr in result.test_results]
    with open(f"eval_results_{label}.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    errors = sum(1 for r in out for m in r["metrics"].values() if m["error"])
    print(f"Saved {len(out)} rows to eval_results_{label}.json ({errors} metric errors)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "local")
