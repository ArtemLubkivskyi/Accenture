"""
Demo 06: The token-cap trap
Block 4 — Run from live_materials/: uv run python code_snippets/06_token_cap_trap.py

Shows: the same call capped at 5 tokens, once with max_tokens and once with
Day 8's max_completion_tokens. Ollama reads only max_tokens and ignores the
other name without an error. The Day 12 cloud model is the mirror image: it
rejects max_tokens. That is why the name is TOKEN_LIMIT_PARAM in config.py.
"""
import sys
sys.path.insert(0, ".")
from config import get_llm_client, LLM_BASE_URL, LLM_MODEL

client = get_llm_client()

PROMPT = "Count from 1 to 40, separated by commas."
CAP = 5

print(f"Endpoint: {LLM_BASE_URL}")
print(f"Model:    {LLM_MODEL}")
print(f"Prompt:   {PROMPT}")
print(f"Cap:      {CAP} tokens\n")

for param in ["max_tokens", "max_completion_tokens"]:
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": PROMPT}],
        temperature=0.0,
        reasoning_effort="none",
        **{param: CAP},
    )
    text = response.choices[0].message.content.strip().replace("\n", " ")
    print(f"=== {param}={CAP} ===")
    print(f"Output tokens:  {response.usage.completion_tokens}")
    print(f"Finish reason:  {response.choices[0].finish_reason}")
    print(f"Answer:         {text[:90]}{'...' if len(text) > 90 else ''}")
    print()

print("→ No error, no warning. The second cap simply did not exist for Ollama.")
