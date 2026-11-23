"""
Shared config for all demo scripts.
Defaults to local Ollama. Set env vars to switch to another server or to cloud.
"""
import os
from openai import OpenAI

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen3.5:4b-q4_K_M")

# Ollama reads only max_tokens; the Day 12 cloud model rejects it and wants
# max_completion_tokens.
TOKEN_LIMIT_PARAM = os.getenv("TOKEN_LIMIT_PARAM", "max_tokens")

EMBED_BASE_URL = os.getenv("EMBED_BASE_URL", "http://localhost:11434/v1")
EMBED_API_KEY = os.getenv("EMBED_API_KEY", "ollama")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

# Must match the server's context (OLLAMA_CONTEXT_LENGTH or num_ctx); a
# request cannot change it through the OpenAI client.
CONTEXT_LENGTH = int(os.getenv("CONTEXT_LENGTH", "8192"))

# Same variable names as the Day 8 .env, so loading that file is enough.
CLOUD_BASE_URL = os.getenv("AZURE_OPENAI_ENDPOINT", "")
CLOUD_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
CLOUD_MODEL = os.getenv("CLOUD_MODEL", "gpt-5.6-luna")
CLOUD_TOKEN_LIMIT_PARAM = os.getenv("CLOUD_TOKEN_LIMIT_PARAM", "max_completion_tokens")


def get_llm_client() -> OpenAI:
    return OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)


def get_embed_client() -> OpenAI:
    return OpenAI(base_url=EMBED_BASE_URL, api_key=EMBED_API_KEY)


def get_cloud_client() -> OpenAI | None:
    if not (CLOUD_BASE_URL and CLOUD_API_KEY):
        return None
    return OpenAI(base_url=CLOUD_BASE_URL, api_key=CLOUD_API_KEY)
