"""Demo 07, Block 3 slide "Retrieval metrics without a judge": Hit@5 and MRR in plain Python.

Compares the labelled source_document in test_questions.json with the sources the pipeline
retrieved (context_sources in pipeline_outputs.json). No API calls, same result on every run.
Questions labelled with several documents, or none (unanswerable), are skipped.

    uv run python code_snippets/07_retrieval_metrics.py path/to/test_questions.json path/to/pipeline_outputs.json
    uv run python code_snippets/07_retrieval_metrics.py --example     # made-up retrievals, no files needed
"""

import json
import sys

EXAMPLE_QUESTIONS = [
    {"id": "q01", "source_document": "company_handbook.pdf"},
    {"id": "q02", "source_document": "security_policy.pdf"},
    {"id": "q03", "source_document": "product_guide.pdf"},
    {"id": "q15", "source_document": None},
]
EXAMPLE_OUTPUTS = [
    {"id": "q01", "context_sources": [{"source": s} for s in
                                      ["company_handbook.pdf", "meeting_notes.pdf", "product_guide.pdf"]]},
    {"id": "q02", "context_sources": [{"source": s} for s in
                                      ["product_guide.pdf", "meeting_notes.pdf", "security_policy.pdf",
                                       "company_handbook.pdf", "product_guide.pdf"]]},
    {"id": "q03", "context_sources": [{"source": s} for s in
                                      ["meeting_notes.pdf", "company_handbook.pdf", "security_policy.pdf"]]},
    {"id": "q15", "context_sources": [{"source": "company_handbook.pdf"}]},
]


def load(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


if "--example" in sys.argv or len(sys.argv) < 3:
    if "--example" not in sys.argv:
        print("No files given, using the made-up example. Pass test_questions.json and pipeline_outputs.json.\n")
    questions, rows = EXAMPLE_QUESTIONS, EXAMPLE_OUTPUTS
else:
    questions, rows = load(sys.argv[1]), load(sys.argv[2])

labels = {q["id"]: q.get("source_document") for q in questions}
ranks = []
print(f"{'id':<6} {'labelled source':<30} rank")
for r in rows:
    label = labels.get(r["id"])
    if label in (None, "", "multiple") or isinstance(label, list):
        continue
    sources = [c["source"] for c in r["context_sources"]][:5]
    rank = sources.index(label) + 1 if label in sources else None
    ranks.append(rank)
    print(f"{r['id']:<6} {label:<30} {rank if rank else 'not in top 5'}")

if not ranks:
    raise SystemExit("No question with a single labelled source document.")
hit_at_5 = sum(rk is not None for rk in ranks) / len(ranks)
mrr = sum(1 / rk for rk in ranks if rk) / len(ranks)
print(f"\nQuestions scored: {len(ranks)}   Hit@5: {hit_at_5:.2f}   MRR: {mrr:.2f}")
print("Hit@5: the right document is somewhere in the top 5. MRR: the average of 1/rank, 1.0 means always first.")
