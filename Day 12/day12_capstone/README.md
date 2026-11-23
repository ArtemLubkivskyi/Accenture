# Day 12: Evaluating my local RAG pipeline

I evaluated my own Day 11 pipeline ([`Day 11/local-rag`](../../Day%2011/local-rag)), not the reference one. Everything ran on the same 19 test questions (16 with a known source document, 3 with no answer in the documents).

- **Local model:** `qwen3.5:4b-q4_K_M` on CPU through Ollama, thinking off
- **Cloud model:** `gpt-5.6-luna` on Azure OpenAI, thinking off
- **Judge:** `gpt-5.4-mini` with DeepEval, five metrics (faithfulness, answer relevancy, contextual relevancy, recall and precision)
- **Retrieval:** the same in both runs (local `nomic-embed-text` + Chroma, top-5), so only the generator changes

AI assistant used: Claude Code, for the scripts (`compare.py`, `check_eval.py`, `retrieval_metrics.py`, my own attacks in `security_probe.py`) and for running the evaluation steps. The report and the security verdicts are written by me.

## Files

| File | What it holds |
|---|---|
| [`evaluation_report.md`](./evaluation_report.md) | The report: findings, local vs cloud, security, recommendations |
| `pipeline_outputs_local.json`, `pipeline_outputs_cloud.json` | Answers from both models, with my hand ratings for the local run |
| `eval_results_local.json`, `eval_results_cloud.json` | DeepEval scores and the judge's reason for every question |
| [`compare_output.md`](./compare_output.md) | Output of `compare.py`: local vs cloud, mean ± 2×SE, speed and tokens |
| `retrieval_metrics_local.txt` | Hit@5 and MRR, computed without a judge |
| `check_local.txt`, `check_cloud.txt` | Every score below 0.7 with the judge's reason |
| `security_results_local.json`, `security_results_cloud.json` | 12 attacks per model, answers and my verdicts |

## How to run

From `Day 11/local-rag`, with Ollama running and the Azure variables from the Day 8 `.env` set:

```
uv run python eval_pipeline.py local
uv run python pipeline.py --test-set pipeline_outputs_cloud.json   # with the LLM_* cloud variables
uv run python eval_pipeline.py cloud
uv run python security_probe.py local
uv run python security_probe.py cloud
uv run python compare.py
uv run python retrieval_metrics.py
```

On Windows, `run_azure_steps.ps1` runs all Azure steps in order and skips the ones whose output file already exists.
