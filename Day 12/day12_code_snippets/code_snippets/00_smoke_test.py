"""Day 12 smoke test: run the evening before and the morning of the session.

One call to the judge, the cloud candidate and the local model, then one DeepEval metric
through the judge. Prints model, latency, tokens and the DeepEval cost. Costs well under a cent.

    uv run python code_snippets/00_smoke_test.py            # all four checks
    uv run python code_snippets/00_smoke_test.py --no-local # skip Ollama
"""

import sys

from _common import CLOUD_MODEL, JUDGE_MODEL, LOCAL_MODEL, chat, deepeval_judge, rule

PING = [{"role": "user", "content": "Reply with the single word: ready"}]
failures = []


def check(label: str, target: str) -> None:
    try:
        r = chat(PING, target=target, max_tokens=256)
        ok = bool(r["text"])
        print(f"{'OK  ' if ok else 'FAIL'} {label:<6} {r['model']:<22} {r['seconds']:>5.1f} s  "
              f"tokens in/out {r['prompt_tokens']}/{r['completion_tokens']}  reasoning {r['reasoning_tokens']}  "
              f"finish {r['finish_reason']}  -> {r['text'][:30]!r}")
        if not ok:
            failures.append(f"{label}: empty answer (finish_reason={r['finish_reason']})")
    except Exception as e:
        print(f"FAIL {label:<6} {type(e).__name__}: {str(e)[:160]}")
        failures.append(label)


rule("Chat completions")
check("judge", "judge")
check("cloud", "cloud")
if "--no-local" not in sys.argv:
    check("local", "local")

rule(f"DeepEval FaithfulnessMetric with {JUDGE_MODEL}")
try:
    from deepeval.metrics import FaithfulnessMetric
    from deepeval.test_case import LLMTestCase

    metric = FaithfulnessMetric(threshold=0.7, model=deepeval_judge(), async_mode=False)
    metric.measure(LLMTestCase(
        input="How many days per week can employees work remotely?",
        actual_output="Up to 3 days per week, with manager approval.",
        retrieval_context=["Employees may work remotely up to 3 days per week with manager approval."],
    ))
    print(f"OK   score {metric.score}  cost {metric.evaluation_cost}  reason: {metric.reason[:100]}")
except Exception as e:
    print(f"FAIL {type(e).__name__}: {str(e)[:200]}")
    failures.append("deepeval")

rule()
print(f"Judge {JUDGE_MODEL} · cloud {CLOUD_MODEL} · local {LOCAL_MODEL}")
print("All checks passed." if not failures else f"Failed: {', '.join(failures)}")
sys.exit(1 if failures else 0)
