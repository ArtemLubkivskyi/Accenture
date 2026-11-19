"""Configuration for the local RAG pipeline.

Every provider setting is an environment variable with a local default, so
swapping from Ollama to a cloud model is configuration only.
"""

import os

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen3.5:4b-q4_K_M")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "http://localhost:11434/v1")
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "ollama")

# RecursiveCharacterTextSplitter counts characters, not tokens:
# 512 characters is about 115 tokens on the provided PDFs.
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K = int(os.getenv("TOP_K", "5"))
COLLECTION_NAME = "bootcamp_docs"
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", "./documents")

SYSTEM_PROMPT = """You are a helpful assistant answering questions based on provided context.
Use ONLY the context below to answer. If the answer is not in the context, say "I cannot find this information in the provided documents."

Context:
{context}"""

# TEMPERATURE=none sends no temperature at all: the GPT-5.x cloud models reject the parameter.
# ("none" rather than empty, because PowerShell deletes a variable set to "".)
_temperature = os.getenv("TEMPERATURE", "0.3").strip().lower()
TEMPERATURE = None if _temperature in ("", "none") else float(_temperature)

# "none" switches thinking off. Thinking and answer share one token cap, so a
# thinking model can spend the whole cap and return an empty answer.
REASONING_EFFORT = os.getenv("REASONING_EFFORT", "none")

# Ollama reads only max_tokens; the Day 12 cloud model rejects it and wants
# max_completion_tokens. The name is configuration so the calls stay the same.
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))
TOKEN_LIMIT_PARAM = os.getenv("TOKEN_LIMIT_PARAM", "max_tokens")
