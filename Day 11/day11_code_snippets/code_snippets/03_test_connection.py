"""
Demo 03: Config swap pattern — test connection
Block 4 — Run from live_materials/: python code_snippets/03_test_connection.py

Shows: Same script works with local (default) or cloud (via env vars).

To switch to the Day 12 cloud model (endpoint and key are the ones in your Day 8 .env):
  export LLM_BASE_URL=https://<resource>.openai.azure.com/openai/v1/
  export LLM_API_KEY=$AZURE_OPENAI_API_KEY
  export LLM_MODEL=gpt-5.6-luna
  export TOKEN_LIMIT_PARAM=max_completion_tokens
"""
import sys
sys.path.insert(0, ".")
from config import get_llm_client, LLM_BASE_URL, LLM_MODEL, TOKEN_LIMIT_PARAM

client = get_llm_client()

print("=== Config Swap Demo ===")
print(f"Endpoint: {LLM_BASE_URL}")
print(f"Model:    {LLM_MODEL}")
print()

response = client.chat.completions.create(
    model=LLM_MODEL,
    messages=[
        {"role": "user", "content": "Say hello and tell me what model you are. One sentence."},
    ],
    temperature=0.3,
    reasoning_effort="none",
    **{TOKEN_LIMIT_PARAM: 100},
)

print("=== Response ===")
print(response.choices[0].message.content)
print()
print(f"→ This ran on: {LLM_BASE_URL}")
print("→ To switch providers, set LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, TOKEN_LIMIT_PARAM env vars.")
print("→ Zero code changes needed.")
