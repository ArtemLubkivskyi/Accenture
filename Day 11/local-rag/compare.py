"""Local vs cloud: reads both eval_results_*.json and pipeline_outputs_*.json, prints markdown.

    uv run python compare.py

Error bars are mean +- 2*SE, SE = sample std / sqrt(n). The verdict uses the per-question
difference (cloud - local on the same id), so question difficulty cancels out.
"""
import json
import math
import statistics


def load(name):
    with open(name, encoding="utf-8") as f:
        return json.load(f)


def mean_2se(values):
    m = statistics.mean(values)
    if len(values) < 2:
        return m, float("nan")
    return m, 2 * statistics.stdev(values) / math.sqrt(len(values))


def scores(eval_rows, metric):
    # id -> score, skipping rows where the metric errored
    out = {}
    for r in eval_rows:
        m = r["metrics"].get(metric)
        if m and m["score"] is not None:
            out[r["id"]] = m["score"]
    return out


local_eval, cloud_eval = load("eval_results_local.json"), load("eval_results_cloud.json")
local_out, cloud_out = load("pipeline_outputs_local.json"), load("pipeline_outputs_cloud.json")

metric_names = []
for r in local_eval:
    for name in r["metrics"]:
        if name not in metric_names:
            metric_names.append(name)

print("| Metric | n | Local | Cloud | Cloud - Local | Verdict |")
print("|---|---|---|---|---|---|")
big_gaps = {}
for metric in metric_names:
    loc, cld = scores(local_eval, metric), scores(cloud_eval, metric)
    ids = sorted(set(loc) & set(cld))
    if not ids:
        print(f"| {metric} | 0 | - | - | - | no data |")
        continue
    lm, ls = mean_2se([loc[i] for i in ids])
    cm, cs = mean_2se([cld[i] for i in ids])
    diffs = [cld[i] - loc[i] for i in ids]
    dm, ds = mean_2se(diffs)
    if math.isnan(ds) or dm - ds <= 0 <= dm + ds:
        verdict = "no clear difference"
    else:
        verdict = "cloud higher" if dm > 0 else "local higher"
    print(f"| {metric} | {len(ids)} | {lm:.2f} ± {ls:.2f} | {cm:.2f} ± {cs:.2f} | "
          f"{dm:+.2f} ± {ds:.2f} | {verdict} |")
    big_gaps[metric] = [(i, cld[i] - loc[i]) for i in ids if abs(cld[i] - loc[i]) >= 0.3]

print("\nQuestions where cloud and local differ by 0.3 or more:")
for metric, gaps in big_gaps.items():
    if gaps:
        print(f"- {metric}: " + ", ".join(f"{i} ({d:+.2f})" for i, d in gaps))


def run_stats(rows):
    times = [r["generation_time_ms"] for r in rows if r.get("generation_time_ms") is not None]
    tokens = [r["tokens_generated"] for r in rows if r.get("tokens_generated") is not None]
    bad = [r["id"] for r in rows
           if not (r.get("actual_answer") or "").strip() or r.get("finish_reason") != "stop"]
    slowest = max(rows, key=lambda r: r.get("generation_time_ms") or 0)
    return {
        "model": rows[0].get("model"),
        "median_s": statistics.median(times) / 1000,
        "slowest": f"{slowest['generation_time_ms'] / 1000:.1f} s ({slowest['id']})",
        "avg_tokens": statistics.mean(tokens) if tokens else float("nan"),
        "bad": f"{len(bad)}" + (f" ({', '.join(bad)})" if bad else ""),
    }


print("\n| Run | Model | Median generation | Slowest | Avg completion tokens | Empty or failed |")
print("|---|---|---|---|---|---|")
for label, rows in (("local", local_out), ("cloud", cloud_out)):
    s = run_stats(rows)
    print(f"| {label} | {s['model']} | {s['median_s']:.1f} s | {s['slowest']} | "
          f"{s['avg_tokens']:.0f} | {s['bad']} |")
print("\nCompletion tokens come from usage.completion_tokens, which includes reasoning tokens when reported.")
