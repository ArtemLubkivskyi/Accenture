"""Model benchmarking: compare models on speed and quality across task types."""

import json
import sys
import time

from openai import OpenAI

import config

MODELS = ["qwen3.5:4b-q4_K_M", "qwen3.5:2b-q4_K_M"]

PROMPTS = [
    {
        "category": "factual",
        "prompt": "What causes tides on Earth? Answer in 2-3 sentences.",
    },
    {
        "category": "reasoning",
        "prompt": "If a train travels 120km in 1.5 hours, and then 80km in 1 hour, what is the average speed for the entire journey?",
    },
    {
        "category": "summarization",
        "prompt": "Summarize the following in 2 sentences: Cloud computing has transformed how businesses operate by providing on-demand access to computing resources without the need for direct active management. The three main service models—Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and Software as a Service (SaaS)—offer different levels of abstraction and management. IaaS provides virtualized computing resources, PaaS provides a platform for application development, and SaaS delivers complete applications over the internet. The shift to cloud has enabled organizations to reduce capital expenditure, improve scalability, and accelerate time to market for new products and services.",
    },
    {
        "category": "structured_output",
        "prompt": 'List 3 European capitals. Respond ONLY with valid JSON: [{"city": "...", "country": "..."}]',
    },
    {
        "category": "code_generation",
        "prompt": "Write a Python function that takes a list of numbers and returns the second largest unique number. Include a docstring.",
    },
    {
        "category": "instruction_following",
        "prompt": "Name 5 programming languages. Format: numbered list, each with exactly one word of description. Example: 1. Python - versatile",
    },
    {
        "category": "rag_simulation",
        "prompt": 'Based on the following context, answer the question.\n\nContext: "The company\'s remote work policy allows employees to work from home up to 3 days per week. All remote work arrangements must be approved by the direct manager. Employees in their first 90 days are required to work on-site full-time."\n\nQuestion: Can a new employee work remotely during their first month?',
    },
]


def run_benchmark(model: str, prompt_item: dict) -> dict:
    client = OpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)

    start = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt_item["prompt"]}],
        temperature=0.7,
        reasoning_effort=config.REASONING_EFFORT,
        **{config.TOKEN_LIMIT_PARAM: config.MAX_TOKENS},
    )
    elapsed = time.time() - start

    choice = response.choices[0]
    content = choice.message.content or ""
    usage = response.usage

    if not content.strip():
        print(
            f"WARNING: empty response from {model} "
            f"(finish_reason={choice.finish_reason}) on {prompt_item['category']}",
            file=sys.stderr,
        )

    return {
        "model": model,
        "category": prompt_item["category"],
        "prompt": prompt_item["prompt"][:100] + "..." if len(prompt_item["prompt"]) > 100 else prompt_item["prompt"],
        "response": content,
        "thinking": config.REASONING_EFFORT != "none",
        "finish_reason": choice.finish_reason,
        "time_seconds": round(elapsed, 2),
        "prompt_tokens": usage.prompt_tokens if usage else None,
        "completion_tokens": usage.completion_tokens if usage else None,
        "tokens_per_second": (
            round(usage.completion_tokens / elapsed, 1)
            if usage and usage.completion_tokens
            else None
        ),
        "quality_rating": None,
        "rating_note": "",
    }


def main():
    results = []
    total = len(MODELS) * len(PROMPTS)
    count = 0

    for model in MODELS:
        print(f"\n{'='*60}")
        print(f"Model: {model}")
        print(f"{'='*60}")
        for prompt_item in PROMPTS:
            count += 1
            print(f"  [{count}/{total}] {prompt_item['category']}...", end=" ", flush=True)
            result = run_benchmark(model, prompt_item)
            results.append(result)
            print(f"{result['time_seconds']}s, {result['tokens_per_second']} tok/s")

    with open("benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved {len(results)} results to benchmark_results.json")
    print("Fill in quality_rating (1-5) and rating_note by hand; re-running overwrites the file.")

    print(f"\n{'Model':<20} {'Category':<22} {'Time (s)':<10} {'Tok/s':<10}")
    print("-" * 62)
    for r in results:
        print(f"{r['model']:<20} {r['category']:<22} {r['time_seconds']:<10} {r['tokens_per_second'] or 'N/A':<10}")


if __name__ == "__main__":
    main()
