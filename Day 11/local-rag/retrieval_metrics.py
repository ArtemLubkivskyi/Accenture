"""Hit@5 and MRR without a judge, from source_document labels and context_sources.

    uv run python retrieval_metrics.py [pipeline_outputs_local.json]

A question labelled with two documents ("a.pdf, b.pdf") counts as a hit if any of them is in
the top 5; the rank is the first position of any labelled document. The last column says
whether all labelled documents were retrieved. Unanswerable questions have no label and are skipped.
"""
import json
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "pipeline_outputs_local.json"
with open(path, encoding="utf-8") as f:
    rows = json.load(f)

ranks = []
print(f"{'id':<5} {'labelled':<48} {'rank':<6} all found")
for r in rows:
    if not r.get("source_document"):
        continue
    wanted = [d.strip() for d in r["source_document"].split(",")]
    got = [c["source"] for c in r["context_sources"]][:5]
    positions = [got.index(d) + 1 for d in wanted if d in got]
    rank = min(positions) if positions else None
    ranks.append(rank)
    all_found = "yes" if len(positions) == len(wanted) else "no"
    print(f"{r['id']:<5} {r['source_document']:<48} {str(rank or '-'):<6} {all_found}")

hit5 = sum(1 for rk in ranks if rk) / len(ranks)
mrr = sum(1 / rk for rk in ranks if rk) / len(ranks)
print(f"\n{len(ranks)} questions with a label. Hit@5 = {hit5:.2f}, MRR = {mrr:.2f}")
