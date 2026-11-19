"""Generation: take retrieved chunks + query and produce an answer via LLM."""

import sys
import time

from openai import OpenAI

import config


def generate_answer(query: str, chunks: list[dict]) -> dict:
    """Returns the answer together with the exact context the model saw and call metadata."""
    context = "\n\n---\n\n".join(
        f"[Source: {chunk['source']}, Page {chunk['page']}]\n{chunk['content']}"
        for chunk in chunks
    )
    system_message = config.SYSTEM_PROMPT.format(context=context)

    client = OpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)

    start = time.time()
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": query},
        ],
        reasoning_effort=config.REASONING_EFFORT,
        **{config.TOKEN_LIMIT_PARAM: config.MAX_TOKENS},
        **({"temperature": config.TEMPERATURE} if config.TEMPERATURE is not None else {}),
    )
    elapsed_ms = round((time.time() - start) * 1000)

    choice = response.choices[0]
    answer = choice.message.content or ""
    usage = response.usage

    if not answer.strip():
        print(
            f"WARNING: empty answer from {config.LLM_MODEL} "
            f"(finish_reason={choice.finish_reason}) for: {query[:60]}",
            file=sys.stderr,
        )

    return {
        "query": query,
        "answer": answer,
        "context_used": context,
        "model": config.LLM_MODEL,
        "thinking": config.REASONING_EFFORT != "none",
        "finish_reason": choice.finish_reason,
        "generation_time_ms": elapsed_ms,
        "tokens_generated": usage.completion_tokens if usage else None,
        "prompt_tokens": usage.prompt_tokens if usage else None,
    }


if __name__ == "__main__":
    test_chunks = [
        {
            "content": "Employees may work remotely up to 3 days per week with prior manager approval.",
            "source": "company_handbook.pdf",
            "page": 5,
        }
    ]
    result = generate_answer("What is the remote work policy?", test_chunks)
    print(f"Answer: {result['answer']}")
    print(f"\nModel: {result['model']} (thinking: {result['thinking']})")
    print(f"Finish reason: {result['finish_reason']}")
    print(f"Generation time: {result['generation_time_ms']}ms")
    print(f"Tokens generated: {result['tokens_generated']}")
