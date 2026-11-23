# Day 11: Local Document Q&A (RAG)

A document Q&A pipeline that runs fully on a laptop. It answers questions about the five NovaTech PDFs in `documents/` using Ollama for both embeddings and generation, so no document text leaves the machine.

AI assistant used: Claude Code (Claude Opus) for writing code. The model inside the pipeline is local (`qwen3.5:4b-q4_K_M`, `nomic-embed-text`).

## Setup

1. Install Ollama (native Windows app) and set the user environment variable `OLLAMA_CONTEXT_LENGTH=8192`, then restart Ollama.
2. Pull the models:
   ```
   ollama pull qwen3.5:4b-q4_K_M
   ollama pull qwen3.5:2b-q4_K_M
   ollama pull nomic-embed-text
   ```
3. Install uv, then in this folder: `uv sync`
4. Check: `uv run python test_api.py` should print one sentence and `finish_reason: stop`. `ollama ps` should show CONTEXT 8192.

## How to run

| Step | Command | Output |
|---|---|---|
| Build the vector DB (rebuilds `chroma_db/`) | `uv run python ingest.py` | `chroma_db/` |
| Look at retrieval only | `uv run python retrieve.py "your question"` | printed chunks |
| Ask one question | `uv run python pipeline.py "your question"` | printed answer |
| Run all test questions | `uv run python pipeline.py --all` | `pipeline_outputs.json` |
| Model benchmark | `uv run python benchmark.py` | `benchmark_results.json` |
| Summary numbers | `uv run python summarize.py` | printed tables |
| Check a PDF page extraction | `uv run python peek_pdf.py product_guide.pdf 14` | printed page |

`chroma_db/` is not committed. `uv run python ingest.py` rebuilds it.

## Files

- `config.py`: every setting (endpoint, models, chunking, top-k, prompt, token cap). Switching to a cloud model only needs `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` and `TOKEN_LIMIT_PARAM` as environment variables.
- `ingest.py`, `retrieve.py`, `generate.py`, `pipeline.py`: the pipeline.
- `test_questions.json`: test questions with expected answers and the pages that contain the answer (`evidence`).
- `benchmark_results.json`, `pipeline_outputs.json`: written by the code, ratings added by hand.
- `decision_log.md`: my choices and reasoning.

All numbers about speed and accuracy are in `decision_log.md` and come from the two JSON files (printed by `summarize.py`).

The Day 12 evaluation scripts are in this folder too, but their results are in [`Day 12/day12_capstone`](../../Day%2012/day12_capstone).
