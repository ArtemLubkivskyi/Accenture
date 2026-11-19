# Reference Implementation: Local RAG Pipeline

This is the reference implementation for the Day 11–12 capstone. It serves two purposes:

1. **Theory demos:** used during the Day 11 theory session for live code demonstrations.
2. **Day 12 baseline:** shared with everyone at the start of Day 12, as a baseline for the evaluation.

It is not handed out on Day 11. Day 11 points come from the student's own pipeline.

**Presenter:** hand out the five PDFs from `../documents/` only. The Markdown sources and `convert_to_pdf.py` in that folder stay with you; with the Markdown in hand, the PDF and table extraction decision disappears.

## Setup

Ollama 0.40.x must be running (`curl http://localhost:11434/api/version` prints a version) with a context window of 8192 (`OLLAMA_CONTEXT_LENGTH=8192`; see Exercise 0 of the capstone brief).

```bash
ollama pull qwen3.5:4b-q4_K_M
ollama pull qwen3.5:2b-q4_K_M
ollama pull nomic-embed-text

uv init --python 3.12
uv add openai chromadb langchain-text-splitters pypdf

mkdir documents
cp ../documents/*.pdf documents/
```

## Usage

### 1. Ingest documents

```bash
uv run python ingest.py
```

Prints 85 pages and 335 chunks for the five PDFs with the default settings. Running it again recreates the collection; the count stays at 335.

### 2. Run a single query

```bash
uv run python pipeline.py "What is the remote work policy?"
```

### 3. Run all test questions

```bash
uv run python pipeline.py --test-set
```

This produces `pipeline_outputs.json`, the input for Day 12 evaluation. One row per question:

| Field | Meaning |
|---|---|
| `id`, `question`, `expected_answer` | From `test_questions.json` |
| `actual_answer` | What the model answered; an empty answer prints a warning |
| `retrieved_context` | The chunk texts, in rank order |
| `context_sources` | `source`, `page`, `score` per chunk |
| `model`, `thinking`, `finish_reason` | Model tag, whether thinking was on, why generation stopped |
| `embedding_model` | Model that embedded the query |
| `prompt_tokens`, `tokens_generated` | From the API's usage block |
| `retrieval_time_ms`, `generation_time_ms` | Wall-clock timings |
| `passed`, `rating_note` | Left as `null` and `""` for a person to fill in after reading the answer: `true` or `false`, and a short reason. Re-running overwrites the file, so rate last. |

### 4. Run benchmarks

```bash
uv run python benchmark.py
```

Writes `benchmark_results.json`: one row per model and prompt with `model`, `category`, `prompt`, `response`, `thinking`, `finish_reason`, `time_seconds`, `prompt_tokens`, `completion_tokens`, `tokens_per_second`, and `quality_rating` / `rating_note`, which are left empty for a person to fill in. Re-running overwrites the file.

## Thinking and the token cap

Every chat call sends `temperature`, `reasoning_effort` (default `"none"`, thinking off) and a token cap. `TEMPERATURE=none` leaves `temperature` out. Set `REASONING_EFFORT=low` to see the same model with thinking on; thinking and answer share the cap.

The cap's parameter name is configuration (`TOKEN_LIMIT_PARAM`, default `max_tokens`): Ollama reads only `max_tokens`, the Day 12 cloud model rejects it and accepts `max_completion_tokens`.

## Provider Swap

To run generation on the Day 12 cloud model, with the endpoint and key from the Day 8 `.env`:

```bash
export LLM_BASE_URL="https://<resource>.openai.azure.com/openai/v1/"
export LLM_API_KEY="$AZURE_OPENAI_API_KEY"
export LLM_MODEL="gpt-5.6-luna"
export TOKEN_LIMIT_PARAM="max_completion_tokens"
uv run python pipeline.py --test-set pipeline_outputs_cloud.json
```

The same in PowerShell on Windows:

```powershell
$env:LLM_BASE_URL = "https://<resource>.openai.azure.com/openai/v1/"
$env:LLM_API_KEY = $env:AZURE_OPENAI_API_KEY
$env:LLM_MODEL = "gpt-5.6-luna"
$env:TOKEN_LIMIT_PARAM = "max_completion_tokens"
uv run python pipeline.py --test-set pipeline_outputs_cloud.json
```

The Day 8 `.env` is not loaded automatically: set `AZURE_OPENAI_API_KEY` in the same shell first. No code changes. Embeddings stay on local Ollama, so the same `chroma_db/` is used. `gpt-5.6-luna` accepts `temperature` only together with `reasoning_effort="none"`, which is the default here. If you turn thinking on for the cloud run, also set `TEMPERATURE=none`. `--test-set` takes an output file name, so the cloud run does not overwrite your hand-rated `pipeline_outputs.json`.

## File Structure

| File | Purpose |
|------|---------|
| `config.py` | All configuration; provider swap via environment variables |
| `ingest.py` | Load PDFs, chunk, embed, store in ChromaDB |
| `retrieve.py` | Query vector DB, return ranked chunks |
| `generate.py` | LLM generation with context |
| `pipeline.py` | End-to-end orchestration |
| `benchmark.py` | Model comparison script |
| `test_questions.json` | 18 Q&A pairs for evaluation |
