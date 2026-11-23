"""
Demo 05: Thinking on vs off, same question
Block 4 — Run from live_materials/: uv run python code_snippets/05_thinking_on_off.py

Shows: the model's default (thinking) against reasoning_effort="none": tokens,
seconds, and where the reasoning text arrives. On Ollama's OpenAI-compatible
endpoint it comes back in message.reasoning, separate from message.content.
"""
import sys
import time
sys.path.insert(0, ".")
from config import get_llm_client, LLM_BASE_URL, LLM_MODEL, TOKEN_LIMIT_PARAM

client = get_llm_client()

QUESTION = (
    "A bat and a ball cost 1.10 euros in total. The bat costs 1.00 euro more "
    "than the ball. How much does the ball cost? Answer in one sentence."
)

RUNS = {
    "model default (parameter left out)": {},
    'reasoning_effort="none"': {"reasoning_effort": "none"},
}

print(f"Endpoint: {LLM_BASE_URL}")
print(f"Model:    {LLM_MODEL}")
print(f"Question: {QUESTION}\n")

for label, extra in RUNS.items():
    start = time.time()
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": QUESTION}],
        temperature=0.3,
        **{TOKEN_LIMIT_PARAM: 4096},
        **extra,
    )
    seconds = time.time() - start
    message = response.choices[0].message
    reasoning = getattr(message, "reasoning", None) or ""

    print(f"=== {label} ===")
    print(f"Seconds:            {seconds:.1f}")
    print(f"Output tokens:      {response.usage.completion_tokens}")
    print(f"Finish reason:      {response.choices[0].finish_reason}")
    print(f"message.reasoning:  {len(reasoning)} characters")
    if reasoning:
        print(f"  starts with:      \"{reasoning[:120].strip()}...\"")
    print(f"message.content:    {message.content.strip()}")
    print()

print("→ Thinking is billed as output tokens and shares the same cap as the answer.")
print("→ In the capstone: reasoning_effort=\"none\" on every call.")
