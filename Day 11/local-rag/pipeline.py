"""End-to-end: question -> retrieve -> generate -> answer.

One question:   uv run python pipeline.py "How many PTO days do employees get?"
All questions:  uv run python pipeline.py --all   (writes pipeline_outputs.json)
"""
import json
import sys

import config
from generate import generate_answer
from retrieve import retrieve_chunks

QUESTIONS_FILE = "test_questions.json"
OUT_FILE = "pipeline_outputs.json"


def answer_question(query):
    retrieval_result = retrieve_chunks(query)
    generation_result = generate_answer(query=query, chunks=retrieval_result["retrieved_chunks"])
    return {**generation_result, "retrieval": retrieval_result}


def to_row(q, result):
    chunks = result["retrieval"]["retrieved_chunks"]
    return {
        "id": q["id"],
        "question": q["question"],
        "expected_answer": q["expected_answer"],
        "source_document": q.get("source_document"),
        "difficulty": q.get("difficulty"),
        "type": q.get("type"),
        "actual_answer": result["answer"],
        "retrieved_context": [c["content"] for c in chunks],
        "context_sources": [
            {"source": c["source"], "page": c["page"], "score": c["relevance_score"]} for c in chunks
        ],
        "model": result["model"],
        "thinking": result["thinking"],
        "finish_reason": result["finish_reason"],
        "embedding_model": result["retrieval"]["embedding_model"],
        "top_k": result["retrieval"]["top_k"],
        "chunk_size_chars": config.CHUNK_SIZE,
        "chunk_overlap_chars": config.CHUNK_OVERLAP,
        "prompt_tokens": result["prompt_tokens"],
        "tokens_generated": result["tokens_generated"],
        "retrieval_time_ms": result["retrieval"]["retrieval_time_ms"],
        "generation_time_ms": result["generation_time_ms"],
        "passed": None,
        "rating_note": "",
    }


def run_all():
    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        questions = json.load(f)

    rows = []
    for q in questions:
        print(f"{q['id']} ({q['difficulty']}, {q['type']}): {q['question']}")
        row = to_row(q, answer_question(q["question"]))
        rows.append(row)
        sources = ", ".join(f"{s['source']} p{s['page']}" for s in row["context_sources"])
        print(f"   -> {row['actual_answer'][:200]}")
        print(f"   [{row['generation_time_ms']} ms, {row['prompt_tokens']} prompt tokens, "
              f"finish={row['finish_reason']}] sources: {sources}\n")
        # save after every question, a full CPU run is slow
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(rows)} rows to {OUT_FILE}")


if __name__ == "__main__":
    if sys.argv[1:] == ["--all"]:
        run_all()
    else:
        query = " ".join(sys.argv[1:]) or "How many PTO days do employees get?"
        result = answer_question(query)
        print(result["answer"])
        print(f"\n[{result['model']}, finish={result['finish_reason']}, "
              f"{result['prompt_tokens']} prompt tokens, {result['generation_time_ms']} ms]")
        for c in result["retrieval"]["retrieved_chunks"]:
            print(f"  {c['source']} p.{c['page']}  score={c['relevance_score']}")
