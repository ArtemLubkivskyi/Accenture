"""Exercise 1: compare local models on speed and quality.

Writes benchmark_results.json. Ratings (quality_rating, rating_note) are filled in by hand afterwards.
uv run python benchmark.py
"""
import json
import time

from openai import OpenAI

import config

MODELS = ["qwen3.5:4b-q4_K_M", "qwen3.5:2b-q4_K_M"]
REASONING_EFFORT = "none"  # same setting for both models, otherwise the comparison is unfair
MAX_TOKENS = 1024
OUT_FILE = "benchmark_results.json"

PROMPTS = [
    {
        "category": "factual",
        "prompt": "What causes tides on Earth? Answer in 2-3 sentences.",
    },
    {
        "category": "reasoning",
        "prompt": "A train travels 120 km in 1.5 hours and then 80 km in 1 hour. "
                  "What is the average speed for the whole journey? Show the calculation briefly.",
    },
    {
        "category": "summarization",
        "prompt": "Summarize this paragraph in exactly one sentence:\n\n"
                  "Each onboarding buddy is a peer from the same or a closely related team who has been at the "
                  "company for at least twelve months and volunteered for the program. Buddies spend at least "
                  "thirty minutes per day with the new hire during the first two weeks and one hour per week in "
                  "months two and three. They give informal advice on team norms, tools and culture, but they are "
                  "not responsible for goals, performance reviews or discipline, which stay with the manager. "
                  "Since the program was formalized in 2022, new-hire attrition dropped by 34%.",
    },
    {
        "category": "structured",
        "prompt": 'List 3 European capitals. Respond ONLY with valid JSON, no markdown: '
                  '[{"city": "...", "country": "...", "population_millions": 0.0}]',
    },
    {
        "category": "code",
        "prompt": "Write a Python function is_palindrome(s) that ignores case, spaces and punctuation. "
                  "Return only the code.",
    },
    {
        "category": "instruction",
        "prompt": "Give exactly 3 tips for staying focused while working from home. "
                  "Each tip must start with a verb, be at most 10 words, and be numbered 1. 2. 3. "
                  "Do not write anything else.",
    },
    {
        "category": "rag_style",
        "prompt": "Context: Employees may work remotely up to three days per week with manager approval. "
                  "Employees in the probationary period may work remotely one day per week.\n\n"
                  "Using ONLY the context, answer: how many remote days can a new employee in the probation "
                  "period take, and what is the dress code? If something is not in the context, say so.",
    },
]

client = OpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)


def ask(model, prompt):
    """Stream one answer and measure time to first token and generation speed."""
    start = time.time()
    first_token = None
    text = ""
    finish_reason = None
    usage = None

    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        reasoning_effort=REASONING_EFFORT,
        stream=True,
        stream_options={"include_usage": True},
        **{config.TOKEN_LIMIT_PARAM: MAX_TOKENS},
    )
    for chunk in stream:
        if chunk.usage:
            usage = chunk.usage
        if not chunk.choices:
            continue
        piece = chunk.choices[0].delta.content
        if piece:
            if first_token is None:
                first_token = time.time()
            text += piece
        if chunk.choices[0].finish_reason:
            finish_reason = chunk.choices[0].finish_reason
    end = time.time()
    return text, finish_reason, usage, start, first_token, end


def run_benchmark(model, item):
    text, finish_reason, usage, start, first_token, end = ask(model, item["prompt"])
    total = end - start
    out_tokens = usage.completion_tokens if usage else None
    gen_time = (end - first_token) if first_token else None

    if not text.strip():
        print(f"  WARNING: empty answer from {model} on {item['category']}, finish_reason={finish_reason}")

    return {
        "model": model,
        "category": item["category"],
        "prompt": item["prompt"],
        "response": text,
        "thinking": REASONING_EFFORT != "none",
        "reasoning_effort": REASONING_EFFORT,
        "finish_reason": finish_reason,
        "time_seconds": round(total, 2),
        "time_to_first_token_s": round(first_token - start, 2) if first_token else None,
        "prompt_tokens": usage.prompt_tokens if usage else None,
        "completion_tokens": out_tokens,
        # generation speed only (after the first token), the usual "eval rate"
        "tokens_per_second": round(out_tokens / gen_time, 1) if out_tokens and gen_time else None,
        # end-to-end speed, includes prompt processing
        "tokens_per_second_total": round(out_tokens / total, 1) if out_tokens else None,
        "quality_rating": None,
        "rating_note": "",
    }


def main():
    results = []
    for model in MODELS:
        print(f"\n=== {model} ===")
        # warm-up so model loading time is not counted in the first prompt
        print("  warming up (not recorded)...")
        ask(model, "Say OK.")
        for item in PROMPTS:
            row = run_benchmark(model, item)
            results.append(row)
            print(f"  {item['category']:<14} {row['time_seconds']:>6}s  "
                  f"{row['tokens_per_second']} tok/s  finish={row['finish_reason']}")

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(results)} rows to {OUT_FILE}")


if __name__ == "__main__":
    main()
