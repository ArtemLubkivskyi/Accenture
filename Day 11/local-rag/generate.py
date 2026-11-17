"""Build the prompt from retrieved chunks and ask the LLM."""
import time

from openai import OpenAI

import config

llm = OpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)


def build_context(chunks):
    # label each chunk with its source so the model (and I) can see where facts come from
    parts = []
    for i, c in enumerate(chunks, 1):
        parts.append(f"[{i}] ({c['source']}, page {c['page']})\n{c['content']}")
    return "\n\n".join(parts)


def generate_answer(query, chunks):
    context = build_context(chunks)
    messages = [
        {"role": "system", "content": config.SYSTEM_PROMPT.format(context=context)},
        {"role": "user", "content": query},
    ]

    start = time.time()
    response = llm.chat.completions.create(
        model=config.LLM_MODEL,
        messages=messages,
        temperature=config.TEMPERATURE,
        reasoning_effort=config.REASONING_EFFORT,
        **{config.TOKEN_LIMIT_PARAM: config.MAX_TOKENS},
    )
    elapsed_ms = round((time.time() - start) * 1000)

    choice = response.choices[0]
    answer = choice.message.content or ""
    if not answer.strip():
        print(f"WARNING: empty answer for '{query}', finish_reason={choice.finish_reason}")

    usage = response.usage
    return {
        "query": query,
        "answer": answer,
        "context_used": context,
        "model": config.LLM_MODEL,
        "thinking": config.REASONING_EFFORT != "none",
        "reasoning_effort": config.REASONING_EFFORT,
        "finish_reason": choice.finish_reason,
        "generation_time_ms": elapsed_ms,
        "prompt_tokens": usage.prompt_tokens if usage else None,
        "tokens_generated": usage.completion_tokens if usage else None,
    }
