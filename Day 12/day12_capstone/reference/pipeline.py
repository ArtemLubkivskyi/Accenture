"""End-to-end RAG pipeline: query → retrieve → generate → answer."""

import json
import sys

from retrieve import retrieve_chunks
from generate import generate_answer


def answer_question(query: str) -> dict:
    retrieval_result = retrieve_chunks(query)
    generation_result = generate_answer(
        query=query,
        chunks=retrieval_result["retrieved_chunks"],
    )
    return {
        **generation_result,
        "retrieval": retrieval_result,
    }


def run_test_set(test_file: str = "test_questions.json", output_file: str = "pipeline_outputs.json"):
    with open(test_file, encoding="utf-8") as f:
        test_questions = json.load(f)

    results = []
    for i, q in enumerate(test_questions):
        print(f"[{i+1}/{len(test_questions)}] {q['question'][:80]}...")
        output = answer_question(q["question"])
        results.append({
            "id": q["id"],
            "question": q["question"],
            "expected_answer": q.get("expected_answer", ""),
            "actual_answer": output["answer"],
            "retrieved_context": [c["content"] for c in output["retrieval"]["retrieved_chunks"]],
            "context_sources": [
                {"source": c["source"], "page": c["page"], "score": c["relevance_score"]}
                for c in output["retrieval"]["retrieved_chunks"]
            ],
            "model": output["model"],
            "thinking": output["thinking"],
            "finish_reason": output["finish_reason"],
            "embedding_model": output["retrieval"]["embedding_model"],
            "prompt_tokens": output["prompt_tokens"],
            "tokens_generated": output["tokens_generated"],
            "retrieval_time_ms": output["retrieval"]["retrieval_time_ms"],
            "generation_time_ms": output["generation_time_ms"],
            "passed": None,
            "rating_note": "",
        })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    empty = [r["id"] for r in results if not r["actual_answer"].strip()]
    print(f"\nSaved {len(results)} results to {output_file}")
    if empty:
        print(f"WARNING: {len(empty)} empty answers: {', '.join(empty)}")
    print("Fill in passed (true/false) and rating_note by hand; re-running overwrites the file.")
    return results


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test-set":
        # --test-set [output file], so a cloud run does not overwrite the hand-rated local file
        run_test_set(output_file=sys.argv[2] if len(sys.argv) > 2 else "pipeline_outputs.json")
    else:
        query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is the remote work policy?"
        result = answer_question(query)
        print(f"\nQuestion: {result['query']}")
        print(f"Answer: {result['answer']}")
        print(f"\nRetrieval: {len(result['retrieval']['retrieved_chunks'])} chunks in {result['retrieval']['retrieval_time_ms']}ms")
        print(f"Generation: {result['generation_time_ms']}ms ({result['model']}, finish_reason={result['finish_reason']})")
        for i, chunk in enumerate(result["retrieval"]["retrieved_chunks"]):
            src = chunk["source"]
            page = chunk["page"]
            score = chunk["relevance_score"]
            print(f"  Chunk {i+1}: {src} p.{page} (score: {score})")
