# Day 11 demo scripts

The scripts shown live in the Day 11 session (local models).

## Setup

1. Install [Ollama](https://ollama.com) and pull the models: `ollama pull qwen3.5:4b-q4_K_M` and `ollama pull nomic-embed-text`. `qwen3.5:2b-q4_K_M` is the smaller fallback.
2. Install [uv](https://docs.astral.sh/uv/), then run `uv sync` in this folder (Python 3.12).
3. Run `uv run python code_snippets/03_test_connection.py` to check that the model answers.

## Scripts

Run any of them from this folder with `uv run python code_snippets/<name>.py`.

| Script | What it shows |
|---|---|
| `01_ollama_chat.py` | A chat completion against local Ollama, with token counts |
| `02_embeddings.py` | Local embeddings with nomic-embed-text and similarity scores |
| `03_test_connection.py` | The same script against local or cloud, switched by environment variables |
| `04_embedding_similarity.py` | A similarity matrix, with and without the `search_query: ` / `search_document: ` prefixes |
| `05_thinking_on_off.py` | One question with thinking on and with `reasoning_effort="none"` |
| `06_token_cap_trap.py` | `max_tokens` against `max_completion_tokens` on Ollama |
| `07_structured_output.py` | A JSON-schema `response_format` on Ollama |
| `08_streaming_speed.py` | Streaming, time to first token and tokens per second |
| `09_context_budget.py` | A RAG prompt that outgrows the context and is cut without an error |
| `10_local_vs_cloud.py` | One `ask()` against Ollama and the cloud model |

`config.py` holds the endpoints and model names. Everything defaults to Ollama on `localhost:11434`; set `LLM_BASE_URL`, `LLM_MODEL` and the other variables in `config.py` to point the scripts elsewhere.

Every chat call sends `reasoning_effort="none"`. Without it a small token cap is spent on thinking and the answer comes back empty.

`09_context_budget.py` assumes the server context is 8192 tokens. If yours differs, set `CONTEXT_LENGTH`.

The cloud half of `10_local_vs_cloud.py` needs `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` from your Day 8 `.env`. Load it into the shell with `set -a; source <path to your Day 8 folder>/.env; set +a`.

## Also in this folder

- `Modelfile`: the `rag-assistant` model from the session, with an 8192 context and the refusal sentence from the capstone. `ollama create rag-assistant -f Modelfile`, then `ollama run rag-assistant --think=false`.
- `flappy_bird_demo/`: the coding-agent demo, to try yourself. See its README.
