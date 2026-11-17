# AGENTS.md

Local RAG over the five NovaTech PDFs in `documents/`. Everything runs on this laptop through Ollama.

## Rules

- Only local Ollama models inside the pipeline. No tags with `cloud` in the name.
- Every chat call passes `reasoning_effort` and the token cap from `config.py`.
- Numbers in `decision_log.md` and `README.md` must come from a file the code wrote
  (`benchmark_results.json`, `pipeline_outputs.json`). Never type a number by hand.
- `quality_rating`, `passed` and `rating_note` are filled in by me after reading the answers.
- The decision log is written by me, not by the assistant.
- Do not touch `.env` and do not commit `chroma_db/` or `.venv/`.

## How to run (from this folder)

```powershell
uv sync
uv run python test_api.py          # model answers, finish_reason should be stop
uv run python benchmark.py         # writes benchmark_results.json
uv run python ingest.py            # rebuilds chroma_db/ from documents/
uv run python retrieve.py "How many PTO days do employees get?"
uv run python pipeline.py "How many PTO days do employees get?"
uv run python pipeline.py --all    # runs test_questions.json, writes pipeline_outputs.json
```

## Check after each step

- `ollama ps` shows the model with CONTEXT 8192.
- No empty answers: the scripts print a WARNING with `finish_reason` if an answer is empty.
- After ingest, the chunk count printed by `ingest.py` stays the same when it runs twice.
