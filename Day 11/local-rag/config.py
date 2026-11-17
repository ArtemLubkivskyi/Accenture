"""All settings in one place. Swapping local -> cloud is done with env variables only."""
import os

# LLM (OpenAI-compatible endpoint, Ollama by default)
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen3.5:4b-q4_K_M")

# Embeddings stay local even when the LLM is swapped, so chroma_db/ can be reused
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "http://localhost:11434/v1")
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "ollama")
# nomic-embed-text expects these task prefixes, Ollama does not add them
QUERY_PREFIX = "search_query: "
DOC_PREFIX = "search_document: "

# Paths
DOCS_DIR = "documents"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "bootcamp_docs"

# Chunking, in characters (RecursiveCharacterTextSplitter counts characters)
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
# "plain" or "layout" (pypdf extraction mode)
PDF_EXTRACTION_MODE = os.getenv("PDF_EXTRACTION_MODE", "plain")

TOP_K = int(os.getenv("TOP_K", "5"))

SYSTEM_PROMPT = """You are a helpful assistant answering questions based on provided context.
Use ONLY the context below to answer. If the answer is not in the context, say "I cannot find this information in the provided documents."

Context:
{context}
"""

TEMPERATURE = 0.3
REASONING_EFFORT = os.getenv("REASONING_EFFORT", "none")
MAX_TOKENS = 1024
# Ollama reads max_tokens, the Day 12 cloud model wants max_completion_tokens
TOKEN_LIMIT_PARAM = os.getenv("TOKEN_LIMIT_PARAM", "max_tokens")
