"""Clients and settings shared by the Day 12 demo scripts.

Everything comes from environment variables, loaded from ../.env:
  AZURE_OPENAI_API_KEY    key for the Foundry resource
  JUDGE_BASE_URL          Foundry URL ending in /openai/v1/ (falls back to AZURE_OPENAI_ENDPOINT)
  JUDGE_MODEL             judge deployment, default gpt-5.4-mini
  CLOUD_MODEL             cloud candidate, default gpt-5.6-luna
  LLM_BASE_URL, LLM_API_KEY, LLM_MODEL   local generator, default Ollama with qwen3.5:4b-q4_K_M
"""

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

JUDGE_MODEL = os.getenv("JUDGE_MODEL", "gpt-5.4-mini")
CLOUD_MODEL = os.getenv("CLOUD_MODEL", "gpt-5.6-luna")
LOCAL_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
LOCAL_API_KEY = os.getenv("LLM_API_KEY", "ollama")
LOCAL_MODEL = os.getenv("LLM_MODEL", "qwen3.5:4b-q4_K_M")

REFUSAL = "I cannot find this information in the provided documents."
RAG_SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions based on provided context.\n"
    f'Use ONLY the context below to answer. If the answer is not in the context, say "{REFUSAL}"\n\n'
    "Context:\n{context}"
)


def foundry_v1_url() -> str:
    url = (os.getenv("JUDGE_BASE_URL") or os.getenv("AZURE_OPENAI_ENDPOINT") or "").rstrip("/")
    if not url:
        raise SystemExit("Set JUDGE_BASE_URL (or AZURE_OPENAI_ENDPOINT) in live_materials/.env")
    # DeepEval's OpenAIModel and the plain OpenAI client both need the v1 path; the classic
    # AzureOpenAI client wants the bare resource URL instead, which is where February's 404 came from.
    if not url.endswith("/openai/v1"):
        url += "/openai/v1"
    return url + "/"


def foundry_key() -> str:
    key = os.getenv("AZURE_OPENAI_API_KEY")
    if not key:
        raise SystemExit("Set AZURE_OPENAI_API_KEY in live_materials/.env")
    return key


def foundry_client() -> OpenAI:
    return OpenAI(base_url=foundry_v1_url(), api_key=foundry_key())


def local_client() -> OpenAI:
    return OpenAI(base_url=LOCAL_BASE_URL, api_key=LOCAL_API_KEY)


def chat(messages: list[dict], target: str = "local", max_tokens: int = 1024, **extra) -> dict:
    """One chat call to "local" (Ollama), "cloud" (gpt-5.6-luna) or "judge" (gpt-5.4-mini).

    Ollama reads only max_tokens and switches thinking off with reasoning_effort="none".
    The GPT-5.x deployments reject temperature and max_tokens and want max_completion_tokens.
    """
    if target == "local":
        client, model = local_client(), LOCAL_MODEL
        params = {"max_tokens": max_tokens, "reasoning_effort": os.getenv("REASONING_EFFORT", "none")}
    else:
        client, model = foundry_client(), JUDGE_MODEL if target == "judge" else CLOUD_MODEL
        params = {"max_completion_tokens": max_tokens, "reasoning_effort": "low"}
    params.update(extra)
    start = time.time()
    response = client.chat.completions.create(model=model, messages=messages, **params)
    choice = response.choices[0]
    usage = response.usage
    details = getattr(usage, "completion_tokens_details", None) if usage else None
    return {
        "model": model,
        "text": (choice.message.content or "").strip(),
        "finish_reason": choice.finish_reason,
        "seconds": round(time.time() - start, 2),
        "prompt_tokens": usage.prompt_tokens if usage else None,
        "completion_tokens": usage.completion_tokens if usage else None,
        "reasoning_tokens": getattr(details, "reasoning_tokens", None) if details else None,
    }


def deepeval_judge():
    from deepeval.models import OpenAIModel

    # The model name must be one DeepEval knows (gpt-5.4-mini is), otherwise it sends
    # temperature and the reasoning deployment answers 400.
    return OpenAIModel(
        model=JUDGE_MODEL,
        base_url=foundry_v1_url(),
        api_key=foundry_key(),
        generation_kwargs={"reasoning_effort": "low"},
    )


def rule(title: str = "") -> None:
    print(f"\n{'=' * 64}\n{title}\n{'=' * 64}" if title else "=" * 64)
