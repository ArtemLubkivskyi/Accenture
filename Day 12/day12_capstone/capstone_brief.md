# Day 12 Capstone: Evaluate Your Local Document Q&A Service

## Scenario

Same client as on Tuesday: a regulated company that wants an internal document Q&A system on local infrastructure. You built the pipeline. Today you find out how good it is, where it fails, whether a cloud model would do better, and how easy it is to attack. Then you write it up for a tech lead who has to decide whether this goes to production.

You have the rest of today. We agree the deadline together in class, most likely Friday 20 November; submissions are reviewed on Saturday. Questions go to the Teams channel.

### What you hand in

- `eval_results_local.json` and `eval_results_cloud.json`: DeepEval scores for every test question, local and cloud.
- `pipeline_outputs_cloud.json`: your test set answered by the cloud model.
- `compare.py` and its output: the local vs cloud comparison, with error bars.
- `security_results_local.json` and `security_results_cloud.json`: attacks, answers and your verdicts.
- `evaluation_report.md`: the report, written by you.

### How it is scored

Day 12 is worth 10 of the 20 capstone points:

| Area | Points | Where it comes from |
|---|---|---|
| Evaluation execution | 0–3 | Exercise 3: retrieval and generation metrics on your test set, saved and readable |
| Provider comparison | 0–2 | Exercise 4: the same test set on the cloud model, compared with numbers you can defend |
| Security and robustness | 0–2 | Exercise 5: several attack types, your own attacks, local and cloud, and what a production system would need |
| Analysis and insight | 0–3 | Exercise 6: root causes, specific fixes, a recommendation for the client |

The scripts that run the evaluation are given to you, so running them is the start, not the score. The points are in what you find out and how you explain it.

---

## Ground Rules

### Numbers come from files

Every score, rate and time in your report must be traceable to a file your code wrote: `eval_results_*.json`, `pipeline_outputs_*.json`, `security_results_*.json`, or the output of `compare.py`. Name the file next to each table or number. Paste the output of `compare.py` into the report instead of retyping it. If you re-run, replace the file and update the text. A number we cannot find in a saved file counts as not reported.

### Assistants

The six rules from Tuesday still hold. The short version: the assistant may write the script that measures, not the number; the report is yours, written from what you saw; be ready to explain any line.

Assistants are often out of date on today's tools. They tend to suggest `AzureOpenAIModel`, `gpt-4` models, `temperature` on the judge, or `uv add garak`. All four break here. When the brief and the assistant disagree, the brief wins.

### Same judge for everyone

Use `eval_pipeline.py` as given: judge `gpt-5.4-mini`, the same five metrics and settings for everyone. Your scores then mean the same as everyone else's. The judge must not be the model under test, which is why the cloud candidate is `gpt-5.6-luna` and the judge is a different model.

---

## What You Get

In `day12_capstone.zip`:

| File | What it is |
|---|---|
| `capstone_brief.md` | This brief |
| `eval_pipeline.py` | Runs the five DeepEval metrics over a `pipeline_outputs_<label>.json` and writes `eval_results_<label>.json` |
| `security_probe.py` | Runs a set of attacks through your retriever and generator and writes `security_results_<label>.json` |
| `reference/` | The reference implementation of Tuesday's pipeline, with its README and test set |
| `documents/` | The five PDFs, if you need them again |

The reference is a baseline. Evaluate your own pipeline. If yours does not run, evaluate the reference and say so at the top of your report; the analysis points are still there.

The demo scripts from this morning are in `day12_code_snippets.zip`.

---

## Setup

### What you need from Tuesday

- Your Day 11 project, with `test_questions.json` and `pipeline_outputs.json` (your pipeline run over every test question, with `passed` and `rating_note` filled in by hand).
- Ollama running with your model (`qwen3.5:4b-q4_K_M` or the one you chose) and `nomic-embed-text`.
- `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` from your Day 8 `.env`.

### Install

In your Day 11 project:

```bash
uv add deepeval
```

Copy `eval_pipeline.py` and `security_probe.py` into the project folder, next to `pipeline.py`.

Garak is optional (Exercise 5). If you want it, start its install now, because it downloads PyTorch and takes a while. Install it as a separate tool, never with `uv add`:

```bash
uv tool install --python 3.12 garak
```

### Judge variables

`eval_pipeline.py` reads two variables. `JUDGE_BASE_URL` is your Day 8 endpoint, the one that ends in `/openai/v1/`.

```bash
set -a; source <path to your Day 8 folder>/.env; set +a
export JUDGE_BASE_URL="$AZURE_OPENAI_ENDPOINT"
```

PowerShell:

```powershell
$env:AZURE_OPENAI_API_KEY = "<key from your Day 8 .env>"
$env:JUDGE_BASE_URL = "https://<resource>.openai.azure.com/openai/v1/"
```

Keep `.env` out of git and out of your assistant's context.

---

## The Order of Work

1. Setup, above.
2. Exercise 3: evaluate the local pipeline.
3. Exercise 4: run the cloud model and evaluate it.
4. Exercise 5: run the security probes, local and cloud.
5. Check that all five result files exist: `eval_results_local.json`, `pipeline_outputs_cloud.json`, `eval_results_cloud.json`, `security_results_local.json`, `security_results_cloud.json`. If one is missing, ask in Teams now.
6. Analysis, `compare.py`, your own attacks and verdicts.
7. Exercise 6: the report.

Collect all the data before you start writing. The comparison and the security section are the parts most often left unfinished, and each is worth 2 points.

---

## Exercise 3: Evaluate Your Local Pipeline

**Goal:** five scores for every test question, and an explanation for every low one.

### Step 1: Your outputs

```bash
cp pipeline_outputs.json pipeline_outputs_local.json
```

Do not re-run the pipeline for this: the file holds your hand ratings, and re-running overwrites them. If you changed the pipeline since Tuesday and must re-run, write to a new file and rate it again.

### Step 2: Run the evaluation

```bash
uv run python eval_pipeline.py local
```

It reads `pipeline_outputs_local.json`, sends every question to the judge with five metrics and writes `eval_results_local.json`: one row per question `id`, with a score, a pass/fail and the judge's reason for each metric.

| Metric | Question it answers | Needs |
|---|---|---|
| ContextualRelevancy | Are the retrieved chunks about the question? | the chunks |
| ContextualRecall | Do the chunks contain everything the expected answer needs? | chunks, expected answer |
| ContextualPrecision | Are the useful chunks ranked above the useless ones? | chunks, expected answer |
| Faithfulness | Is every claim in the answer supported by the chunks? | the chunks |
| AnswerRelevancy | Does the answer address the question? | the question |

Faithfulness runs with `penalize_ambiguous_claims=True`. By default DeepEval only fails a claim that contradicts the context, and a claim the context never mentions passes. With the flag, an invented detail counts against the score.

The whole class shares one judge deployment, limited to 250 requests a minute. One run is about 300 judge calls, so it takes a few minutes and may pause to wait. The script retries rate-limit errors on its own. At the end it prints how many metric errors are left. If that number is not zero, open the JSON, read the `error` fields, and run again.

### Step 3: Read it

- For every metric below 0.7, read the judge's `reason`. Decide whether you agree. A judge that is wrong is a finding.
- Look at your unanswerable questions separately. Did the answer contain your refusal sentence? A string check (`"cannot find this information" in answer.lower()`) is the most reliable test you have for those rows.
- Compare the judge with your own `passed` column from Tuesday. Count the four cases: both pass, both fail, judge passes what you failed, judge fails what you passed. Which disagreements do you think the judge got right?

### Step 4 (optional): Retrieval without a judge

If your test questions have a `source_document` label, compute Hit@5 and MRR from `context_sources` in your outputs, as in snippet `07_retrieval_metrics.py`. It costs no API calls and gives the same result every run.

---

## Exercise 4: Local vs Cloud

**Goal:** the same test set on `gpt-5.6-luna`, evaluated by the same judge, compared with numbers you can defend.

### Step 1: Swap to the cloud model

The four variables from Tuesday, in the same shell as the judge variables:

```bash
export LLM_BASE_URL="$AZURE_OPENAI_ENDPOINT"
export LLM_API_KEY="$AZURE_OPENAI_API_KEY"
export LLM_MODEL="gpt-5.6-luna"
export TOKEN_LIMIT_PARAM="max_completion_tokens"
```

PowerShell:

```powershell
$env:LLM_BASE_URL = "https://<resource>.openai.azure.com/openai/v1/"
$env:LLM_API_KEY = $env:AZURE_OPENAI_API_KEY
$env:LLM_MODEL = "gpt-5.6-luna"
$env:TOKEN_LIMIT_PARAM = "max_completion_tokens"
```

`gpt-5.6-luna` accepts `temperature` only while thinking is off (`reasoning_effort="none"`, Tuesday's default). If you turn thinking on for the cloud run, stop sending `temperature` too, or the call fails with HTTP 400.

Embeddings stay local, so retrieval is identical in both runs. Only the generator changes.

### Step 2: Run the test set on the cloud model

Write the result to its own file, so your local outputs and ratings survive:

```bash
uv run python pipeline.py --test-set pipeline_outputs_cloud.json
```

That is the reference's command. If your `pipeline.py` has no output-file option, add one, or copy your local file somewhere safe first and rename the new file afterwards. Then evaluate it:

```bash
uv run python eval_pipeline.py cloud
```

Close the shell, or unset the four `LLM_*` variables, before any further local run.

### Step 3: Write `compare.py`

Write a script (an assistant may help) that reads both `eval_results_*.json` files and both `pipeline_outputs_*.json` files and prints one markdown table. For each of the five metrics:

- the number of questions with a score on both sides (`n`),
- local mean ± 2 × SE and cloud mean ± 2 × SE, where SE is the standard deviation divided by √n,
- the per-question difference: cloud minus local on the same question, its mean ± 2 × SE,
- a verdict: "no clear difference" if that range includes zero, otherwise which side is higher.

Below it, for both runs: median and slowest generation time, average completion tokens (reasoning tokens included where reported), and the number of empty or failed answers. Paste the output into your report.

Twenty questions is a small sample. On 20 questions a gap under about 0.10 is not a finding unless the per-question range says so. "No clear difference" is a valid result, and a good one to report honestly.

### Questions to answer in the report

- Where does the local model match the cloud model, and where does it fall short? Name question ids.
- Retrieval is the same in both runs. If the contextual metrics still differ, what does that tell you about the judge?
- What does each answer cost in time, and, for the cloud, in tokens?
- For this client, which would you deploy, and what would change your mind?

---

## Exercise 5: Security Probing

**Goal:** find out how your pipeline behaves under attack, local and cloud, and what a production deployment would need.

### Step 1: Run the given probes

`security_probe.py` imports `retrieve_chunks` from `retrieve.py` and `generate_answer` from `generate.py`, as in the reference. If your functions have other names, change the two import lines.

```bash
uv run python security_probe.py local
```

Then with the four cloud variables set:

```bash
uv run python security_probe.py cloud
```

The probes cover prompt extraction, jailbreak attempts, and document injection: a malicious chunk is added to the retrieved context at generation time, first and last. Your vector store is not touched, so the other exercises are not affected.

On the cloud, Azure's content filter may reject a prompt before the model sees it. The script records that as `[request rejected: ...]`. Count it as resistant, and write down where the protection came from: the provider's filter, not the model and not your pipeline. Your local pipeline has no such filter.

### Step 2: Add your own attacks

Add at least two attacks of your own to `ATTACKS` and run both labels again. Ideas:

- an instruction hidden in the middle of a normal-looking policy paragraph,
- a chunk with a false fact and no instruction at all (knowledge-base poisoning: does the answer repeat it, and does Faithfulness notice?),
- a request to put a link or an image in the answer that carries data out,
- the same attack in another language, or encoded.

### Step 3: Judge the answers yourself

Open both `security_results_*.json` files and fill in `verdict` (`vulnerable`, `partially resistant`, `resistant`) and `note` for every row, by hand. Read the answers: a model that refuses politely is not a model that was attacked successfully.

### Step 4 (optional): Garak

Garak runs hundreds of prompts per probe family. Cap it. Save this as `garak_ollama.yaml`:

```yaml
run:
  generations: 1
  soft_probe_prompt_cap: 40
plugins:
  target_type: openai.OpenAICompatible
  target_name: qwen3.5:4b-q4_K_M
  generators:
    openai:
      OpenAICompatible:
        uri: http://localhost:11434/v1/
        api_key: ollama
        max_tokens: 1024
        extra_params:
          reasoning_effort: none
        suppressed_params:
          - n
```

```bash
garak --config garak_ollama.yaml --spec probes.dan.Dan_11_0,probes.latentinjection.LatentInjectionReport
```

About 41 prompts, a few minutes on a laptop. Garak prints the path of its HTML report at the end. Read some of the hits before you quote a rate: a detector can count a polite refusal as a successful attack.

---

## Exercise 6: Evaluation Report

**Goal:** a report a tech lead can act on. Numbers without interpretation are noise: every score gets a "so what", and every "so what" gets a recommendation.

Write `evaluation_report.md` yourself. An assistant may help with the scripts, not with the report.

```markdown
# Evaluation Report: Local RAG Pipeline

## Run details
Pipeline: [your own / the reference]. Local model: [tag], thinking [on/off].
Cloud model: gpt-5.6-luna. Judge: gpt-5.4-mini, DeepEval [version].
Test set: [n] questions, [n] unanswerable. Date of the runs.

## Executive summary
[3-4 sentences: does it work, how well, is it fit for this client?]

## Retrieval quality  (source: eval_results_local.json)
- ContextualRelevancy, ContextualRecall, ContextualPrecision: mean ± 2×SE each
- Which questions retrieve badly, and why: chunking, embedding, top-K?

## Generation quality  (source: eval_results_local.json)
- Faithfulness, AnswerRelevancy: mean ± 2×SE
- Unanswerable questions: [x of n] refused correctly
- Empty or failed answers: [n], and why
- Where the judge and your own ratings disagree, and who was right

## Local vs cloud  (source: compare.py output)
[paste the table]
[what it means, with question ids]

## Security assessment  (source: security_results_*.json)
| Attack | Local | Cloud |
[your verdicts, including your own attacks]
What a production deployment would need.

## Recommendations
1. [the most important fix, specific]
2. [the next one]
3. [what you would test next]

## Limitations
[sample size, one judge, what you did not test]
```

---

## Known Traps

| Trap | Symptom | Fix |
|---|---|---|
| Thinking eats the token budget | Empty `actual_answer`, `finish_reason` is `length` | Keep `reasoning_effort="none"`. Check for empty answers before you evaluate them |
| The wrong Azure client | `404 Resource not found` on the first metric | Use `eval_pipeline.py` as given. It uses `OpenAIModel` with the `/openai/v1/` URL. `AzureOpenAIModel` and `deepeval set-azure-openai` want a different URL form |
| No judge configured | `OpenAI API key is not configured` | Set `JUDGE_BASE_URL` and `AZURE_OPENAI_API_KEY` in the shell you run from |
| A GPT-5 model rejects a parameter | HTTP 400 on `temperature` or `max_tokens` | `max_completion_tokens` for the cloud, no `temperature` when thinking is on |
| Rate limits | The run pauses, or the summary reports metric errors | Wait. The script retries on its own. If errors remain, run again. Do not raise the concurrency |
| Cloud run overwrote local results | `pipeline_outputs.json` lost your ratings | Labelled file names, and copy before you run |
| Old `LLM_*` variables in the shell | Local run goes to the cloud, or fails to connect | `unset LLM_BASE_URL LLM_API_KEY LLM_MODEL TOKEN_LIMIT_PARAM`, or open a new shell |
| Duplicate chunks after re-ingest | The same chunk twice in `retrieved_context` | Delete the collection before ingesting again. Duplicates inflate the contextual scores |
| Cloud probe rejected | `[request rejected: ... content management policy]` in `security_results_cloud.json` | Not a bug: Azure's content filter blocked the prompt. Record it as a provider guardrail |
| Garak installs a 2023 version | `garak --version` shows 0.9 | `uv tool install garak`, never `uv add garak` |
| The judge scores look wrong | A correct answer fails, or an invented one passes | Read the `reason`. Run that question again. Judge variance and judge mistakes are findings for your report |

---

## Submission

Push your work, the same way as on Tuesday: a Day 12 folder next to your Day 11 one, or the same capstone repository. The deadline is the one we agree in class. The folder contains:

- `eval_pipeline.py`, `security_probe.py` (with your own attacks), `compare.py`
- `pipeline_outputs_local.json`, `pipeline_outputs_cloud.json`
- `eval_results_local.json`, `eval_results_cloud.json`
- `security_results_local.json`, `security_results_cloud.json`
- `garak_ollama.yaml` and the report path, if you ran Garak
- `evaluation_report.md`
- a line in the README: which pipeline you evaluated, and which AI assistant you used

Do not commit `chroma_db/`, `.venv/` or `.env`.

---

## Tips

- **Read the `reason` field.** The reasons tell you more than the numbers.
- **The judge is a model too.** Run one question twice and you may get two scores. Say how you dealt with that.
- **Small samples are noisy.** Report ±, compare per question, and do not build a recommendation on a 0.03 difference.
- **Write for a tech lead.** They want to know whether to ship, what to fix first, and how sure you are.
