# Day 12 demo scripts

The scripts shown live in the Day 12 session (evaluation). Each one prints its result.

## Setup

1. Install [uv](https://docs.astral.sh/uv/), then run `uv sync` in this folder (Python 3.12).
2. Copy `.env.example` to `.env` and fill in the key and endpoint from your Day 8 `.env`. The endpoint ends in `/openai/v1/`.
3. For the local scripts, Ollama must be running with `qwen3.5:4b-q4_K_M` and `nomic-embed-text`.
4. Run `uv run python code_snippets/00_smoke_test.py`. It checks the judge, the cloud model and the local model.

If an old `LLM_BASE_URL` from Tuesday is still set in your shell, it overrides the default: `unset LLM_BASE_URL LLM_MODEL LLM_API_KEY`.

## Scripts

Run any of them from this folder with `uv run python code_snippets/<name>.py`.

| Script | Slide | What it shows | Needs |
|---|---|---|---|
| `00_smoke_test.py` | | One call to judge, cloud and local model, and one DeepEval metric | Foundry, Ollama |
| `01_metrics_comparison.py` | What word-overlap metrics see | BLEU, ROUGE and BERTScore rank a wrong answer above correct paraphrases | nothing (downloads a 1.4 GB model once) |
| `02_scratch_judge.py` | Live demo: a judge from scratch | A judge is a prompt with a rubric | Foundry |
| `03_deepeval_verbose.py` | Same slide | What DeepEval's Faithfulness does per claim, and where its prompts live | Foundry |
| `04_vague_vs_grounded.py` | Vague prompt vs grounded rubric | The same two answers through two judge prompts | Foundry |
| `05_idk_vs_fabrication.py` | "I don't know" vs fabrication | A refusal instruction, and checking for it with a string (`--cloud` for gpt-5.6-luna) | Ollama or Foundry |
| `06_faithfulness_cases.py` | The unanswerable question test | Faithfulness with and without `penalize_ambiguous_claims` | Foundry |
| `07_retrieval_metrics.py` | Retrieval metrics without a judge | Hit@5 and MRR, no API (`--example`, or your `test_questions.json` and `pipeline_outputs_local.json`) | nothing |
| `08_demo_injection.py` | Demo: document injection | Three attacks against the reference pipeline | Ollama, reference |
| `09_difference_real.py` | Is the difference real? | Mean ± 2·SE and the per-question difference (`--example`, or your two `eval_results_*.json`) | nothing |

`_common.py` holds the clients and model names. Judge `gpt-5.4-mini`, cloud `gpt-5.6-luna`, local `qwen3.5:4b-q4_K_M`.

`08_demo_injection.py` imports the reference pipeline from `day12_capstone.zip`. Set `REFERENCE_DIR` to its `reference/` folder.
