"""Exercise 3 checks on one run: scores below 0.7, refusals on unanswerable questions,
and the judge against my own passed column.

    uv run python check_eval.py local

"Judge pass" here = Faithfulness and Answer Relevancy both passed (the two metrics about the
answer itself; the contextual ones grade retrieval, which my hand rating did not).
"""
import json
import math
import statistics
import sys

label = sys.argv[1] if len(sys.argv) > 1 else "local"
with open(f"eval_results_{label}.json", encoding="utf-8") as f:
    evals = {r["id"]: r for r in json.load(f)}
with open(f"pipeline_outputs_{label}.json", encoding="utf-8") as f:
    outputs = json.load(f)

REFUSAL = "cannot find this information"
ANSWER_METRICS = ("Faithfulness", "Answer Relevancy")

print(f"== Means ({label}), mean ± 2*SE")
names = list(next(iter(evals.values()))["metrics"])
for name in names:
    vals = [r["metrics"][name]["score"] for r in evals.values()
            if name in r["metrics"] and r["metrics"][name]["score"] is not None]
    se2 = 2 * statistics.stdev(vals) / math.sqrt(len(vals)) if len(vals) > 1 else float("nan")
    print(f"{name:<22} {statistics.mean(vals):.2f} ± {se2:.2f}  (n={len(vals)})")

print("\n== Scores below 0.7, with the judge's reason")
for rid, r in evals.items():
    for name, m in r["metrics"].items():
        if m["error"]:
            print(f"{rid} {name}: ERROR {m['error'][:120]}")
        elif m["score"] is not None and m["score"] < 0.7:
            print(f"{rid} {name} = {m['score']:.2f}: {(m['reason'] or '')[:300]}")

print("\n== Unanswerable questions (string check)")
for row in outputs:
    if row.get("type") == "unanswerable":
        refused = REFUSAL in row["actual_answer"].lower()
        print(f"{row['id']}: refused={refused}  -> {row['actual_answer'][:120]!r}")

if any(row.get("passed") is not None for row in outputs):
    print("\n== Judge vs my rating")
    cases = {"both pass": [], "both fail": [], "judge pass, I failed": [], "judge fail, I passed": []}
    for row in outputs:
        ms = evals[row["id"]]["metrics"]
        if any(ms.get(n, {}).get("score") is None for n in ANSWER_METRICS):
            print(f"{row['id']}: skipped, a metric errored - re-run eval_pipeline.py")
            continue
        judge_ok = all(ms.get(n, {}).get("success") for n in ANSWER_METRICS)
        me_ok = bool(row["passed"])
        key = ("both pass" if me_ok else "judge pass, I failed") if judge_ok else \
              ("judge fail, I passed" if me_ok else "both fail")
        cases[key].append(row["id"])
    for key, ids in cases.items():
        print(f"{key:<22} {len(ids):>2}  {', '.join(ids)}")
