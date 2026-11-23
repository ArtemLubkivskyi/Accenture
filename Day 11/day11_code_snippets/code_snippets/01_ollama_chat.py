"""
Demo 01: Chat with a local model via Ollama
Block 4 — Run from live_materials/: python code_snippets/01_ollama_chat.py

Shows: Same OpenAI SDK, local endpoint. Three lines changed from Day 8.

Endpoint and model come from config.py (default: Ollama on localhost:11434).
To run against another Ollama server:
  export LLM_BASE_URL=http://<host>:11434/v1
"""
import sys
sys.path.insert(0, ".")
from config import get_llm_client, LLM_BASE_URL, LLM_MODEL, TOKEN_LIMIT_PARAM

client = get_llm_client()

response = client.chat.completions.create(
    model=LLM_MODEL,
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Be concise."},
        {"role": "user", "content": "What is quantization in the context of LLMs? Answer in 2 sentences."},
    ],
    temperature=0.7,
    reasoning_effort="none",
    **{TOKEN_LIMIT_PARAM: 500},
)

print("=== Response Metadata ===")
print(f"Endpoint:       {LLM_BASE_URL}")
print(f"Model:          {response.model}")
print(f"Finish reason:  {response.choices[0].finish_reason}")
print(f"Input tokens:   {response.usage.prompt_tokens}")
print(f"Output tokens:  {response.usage.completion_tokens}")
print(f"Total tokens:   {response.usage.total_tokens}")
print()
print("=== The Answer ===")
print(response.choices[0].message.content)
