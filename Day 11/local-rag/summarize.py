"""Print summary tables from benchmark_results.json and pipeline_outputs.json.

Use these printed numbers in decision_log.md, so every figure comes from a file.
uv run python summarize.py
"""
import json
from collections import defaultdict
from statistics import mean


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"({path} not found)\n")
        return []


bench = load("benchmark_results.json")
if bench:
    print("=== benchmark_results.json ===")
    by_model = defaultdict(list)
    for r in bench:
        by_model[r["model"]].append(r)
    print(f"{'model':<22}{'thinking':>9}{'rows':>6}{'avg s':>8}{'avg tok/s':>11}{'avg TTFT s':>12}{'avg rating':>12}")
    for model, rows in by_model.items():
        rated = [r["quality_rating"] for r in rows if r["quality_rating"] is not None]
        avg_rating = f"{mean(rated):.2f}" if rated else "not rated"
        print(f"{model:<22}{str(rows[0]['thinking']):>9}{len(rows):>6}"
              f"{mean(r['time_seconds'] for r in rows):>8.1f}"
              f"{mean(r['tokens_per_second'] for r in rows):>11.1f}"
              f"{mean(r['time_to_first_token_s'] for r in rows):>12.1f}"
              f"{avg_rating:>12}")
    print()

out = load("pipeline_outputs.json")
if out:
    print("=== pipeline_outputs.json ===")
    print(f"model: {out[0]['model']}, thinking: {out[0]['thinking']}, top_k: {out[0]['top_k']}, "
          f"chunk: {out[0]['chunk_size_chars']} chars / overlap {out[0]['chunk_overlap_chars']} chars")
    print(f"questions: {len(out)}")
    print(f"finish_reason counts: {dict((k, sum(r['finish_reason'] == k for r in out)) for k in set(r['finish_reason'] for r in out))}")
    print(f"empty answers: {sum(not r['actual_answer'].strip() for r in out)}")
    print(f"prompt_tokens: min {min(r['prompt_tokens'] for r in out)}, "
          f"avg {mean(r['prompt_tokens'] for r in out):.0f}, max {max(r['prompt_tokens'] for r in out)}")
    print(f"generation_time_ms: avg {mean(r['generation_time_ms'] for r in out):.0f}, "
          f"max {max(r['generation_time_ms'] for r in out)}")
    print(f"retrieval_time_ms: avg {mean(r['retrieval_time_ms'] for r in out):.0f}")

    # did the expected page show up in the top-k? (only for questions with evidence)
    with open("test_questions.json", encoding="utf-8") as f:
        evidence = {q["id"]: q.get("evidence", []) for q in json.load(f)}
    hits = []
    for r in out:
        ev = evidence.get(r["id"], [])
        if ev:
            got = {(s["source"], s["page"]) for s in r["context_sources"]}
            need = {(e["source"], e["page"]) for e in ev}
            hits.append((r["id"], len(got & need), len(need)))
    print("\nexpected pages found in top-k (found/expected):")
    print("  " + "  ".join(f"{i}:{a}/{b}" for i, a, b in hits))

    rated = [r for r in out if r["passed"] is not None]
    print(f"\npassed: {sum(r['passed'] is True for r in out)} of {len(rated)} rated "
          f"({len(out) - len(rated)} not rated yet)")
    by_diff = defaultdict(list)
    for r in rated:
        by_diff[r["difficulty"]].append(r["passed"])
    for d, vals in by_diff.items():
        print(f"  {d}: {sum(vals)}/{len(vals)}")
