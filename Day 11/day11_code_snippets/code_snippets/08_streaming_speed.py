"""
Demo 08: Streaming, time to first token and tokens per second
Block 4 — Run from live_materials/: uv run python code_snippets/08_streaming_speed.py

Shows: the answer arriving token by token, measured on the client. Time to
first token is mostly prompt processing; tokens per second after that is
generation, the number that memory bandwidth decides.
"""
import sys
import time
sys.path.insert(0, ".")
from config import get_llm_client, LLM_BASE_URL, LLM_MODEL, TOKEN_LIMIT_PARAM

client = get_llm_client()

print(f"Endpoint: {LLM_BASE_URL}")
print(f"Model:    {LLM_MODEL}\n")
print("=== Streaming ===")

start = time.time()
first_token_at = None
chunks = 0
usage = None

stream = client.chat.completions.create(
    model=LLM_MODEL,
    messages=[{"role": "user", "content": "Explain in about 120 words why LLM inference on a laptop is limited by memory bandwidth."}],
    temperature=0.7,
    reasoning_effort="none",
    stream=True,
    stream_options={"include_usage": True},
    **{TOKEN_LIMIT_PARAM: 400},
)

for chunk in stream:
    if chunk.usage:
        usage = chunk.usage
    if not chunk.choices:
        continue
    text = chunk.choices[0].delta.content
    if text:
        if first_token_at is None:
            first_token_at = time.time()
        chunks += 1
        print(text, end="", flush=True)

end = time.time()
generated = usage.completion_tokens if usage else chunks
generation_seconds = end - first_token_at

print("\n")
print("=== Measured on the client ===")
print(f"Time to first token:  {first_token_at - start:.2f} s")
print(f"Generation time:      {generation_seconds:.2f} s")
print(f"Output tokens:        {generated}" + ("" if usage else " (counted chunks, server sent no usage)"))
print(f"Tokens per second:    {generated / generation_seconds:.1f}")
print(f"Total:                {end - start:.2f} s")
print("\n→ Compare with `ollama run <model> --verbose`: eval rate there is the same number.")
