"""
Demo 10: Local vs cloud, one function
Block 4 — Run from live_materials/: uv run python code_snippets/10_local_vs_cloud.py

Shows: the same ask() against local Ollama and, if the Day 8 Azure variables
are set, against the Day 12 cloud model. The only thing that differs per
provider is the client, the model name and the name of the token cap.

For the cloud half, load the Day 8 .env into the shell first:
  set -a; source ../../../day_08_genai_fundamentals/theory/live_materials/.env; set +a
"""
import sys
import time
from openai import APIConnectionError
sys.path.insert(0, ".")
from config import (
    get_cloud_client, get_llm_client,
    CLOUD_MODEL, CLOUD_TOKEN_LIMIT_PARAM, LLM_BASE_URL, LLM_MODEL, TOKEN_LIMIT_PARAM,
)

CONTEXT = "Employees may work remotely up to 3 days per week with manager approval."
QUESTION = "How many days per week can I work from home, and what do I need?"


def ask(client, model, token_param):
    start = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": f"Answer in one sentence from this context only:\n{CONTEXT}"},
            {"role": "user", "content": QUESTION},
        ],
        temperature=0.3,
        reasoning_effort="none",
        **{token_param: 200},
    )
    return response, time.time() - start


def show(label, token_param, response, seconds):
    print(f"=== {label} ===")
    print(f"Model:          {response.model}")
    print(f"Cap parameter:  {token_param}")
    print(f"Seconds:        {seconds:.2f}")
    print(f"Tokens in/out:  {response.usage.prompt_tokens} / {response.usage.completion_tokens}")
    print(f"Answer:         {response.choices[0].message.content.strip()}")
    print()


print(f"Question: {QUESTION}\n")

try:
    response, seconds = ask(get_llm_client(), LLM_MODEL, TOKEN_LIMIT_PARAM)
    show(f"Local ({LLM_BASE_URL})", TOKEN_LIMIT_PARAM, response, seconds)
except APIConnectionError:
    print("=== Local ===")
    print(f"Skipped: nothing answers at {LLM_BASE_URL}. Is Ollama running?\n")

cloud = get_cloud_client()
if cloud is None:
    print("=== Cloud ===")
    print("Skipped: AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY are not set.")
else:
    response, seconds = ask(cloud, CLOUD_MODEL, CLOUD_TOKEN_LIMIT_PARAM)
    show("Cloud (Azure OpenAI)", CLOUD_TOKEN_LIMIT_PARAM, response, seconds)

print("→ Same function, same messages. Day 12 runs your whole test set through both sides.")
