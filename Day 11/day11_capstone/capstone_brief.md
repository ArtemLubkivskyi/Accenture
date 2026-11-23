# Day 11 Capstone: Build a Local Document Q&A Service

## Scenario

Your client operates in a regulated industry and **cannot send proprietary data to cloud AI providers**. They need an internal document Q&A system that runs entirely on local infrastructure. Your task: build a working RAG pipeline using local LLMs that answers questions about a provided document set, and justify every technical decision you make.

On Day 12 (Thursday 19 November) you will formally evaluate this system: retrieval quality, generation accuracy, security, and a comparison with a cloud model. **Design your pipeline with evaluation in mind.** Wednesday 18 November is a public holiday and nothing is scheduled. You may use it as an optional extra day for the build and the decision log; questions posted in the Teams channel that day get answered.

---

## What You Will Build

A Python application with three modules:

1. **Ingestion & Retrieval:** Load PDFs, chunk them, embed with a local model, store in a vector database, and retrieve relevant chunks for a query.
2. **Generation:** Take retrieved chunks + user query, generate an answer using a local LLM via OpenAI-compatible API.
3. **Configuration:** A single config file that controls which LLM provider, model, embedding model, and parameters are used. Swapping from local to cloud should require changing only this config.

Plus three artifacts:
- A **benchmark results file** (`benchmark_results.json`) comparing at least 2 models on speed and quality.
- A **pipeline outputs file** (`pipeline_outputs.json`): your pipeline run over all of your test questions. Day 12 evaluates this file.
- A **decision log** (a simple markdown file) documenting your choices and reasoning.

### How it is scored

Day 11 is worth 10 points across four areas: technical execution, model and architecture decisions, test question quality, and communication and tradeoff awareness. Day 12 adds 10 more for the evaluation.

---

## Ground Rules

### Local only

The model inside your pipeline runs on your machine. **No cloud-tagged Ollama models** (tags with `cloud` in the name, or the cloud badge in the Ollama library): a cloud model behind `localhost` sends the client's documents away and defeats the scenario. While a model is loaded, run `ollama ps` and paste its output (name, size, processor, context) into your decision log.

### Numbers come from files

Every number in your decision log and README (tokens per second, response times, how many test questions passed, retrieval scores) must be traceable to a file in your submission that your code wrote:

- `benchmark_results.json` for Exercise 1,
- `pipeline_outputs.json` (your pipeline run over all of `test_questions.json`) for Exercise 2.

Next to each number or table, name the file and, where it helps, the question `id` or model. Each row in those files records the model tag, whether thinking was on, and `finish_reason`. If you re-run and the numbers change, replace the file and update the text. A number we cannot find in a saved file counts as not reported. Hand-entered ratings are fine, as long as the response they rate is in the same row: `quality_rating` and `rating_note` in `benchmark_results.json`, `passed` and `rating_note` in `pipeline_outputs.json`.

### Assistants on the capstone: six rules

You may use any AI coding assistant. The rubric scores your decisions, so the assistant can type, but it cannot decide, measure or explain for you.

1. **Say what you used.** One line in the README: tool and model. The model inside your *pipeline* must be local (no cloud tags); the assistant that helps you *write* the pipeline can be anything.
2. **Start with an `AGENTS.md`.** How to run each script, the check you use, and the rules of this brief (local models only, numbers come from files). Commit it first.
3. **One step at a time, and commit each one.** Ingest, retrieve, generate, benchmark. Run every step yourself before asking for the next. Small commits let you go back when an assistant breaks something that worked.
4. **The assistant may write the script that measures. It may not write the number.** Every figure in your decision log comes from a file your code wrote. If a summary says "15 of 15 questions answered correctly", open `pipeline_outputs.json` and count the rows you marked `"passed": true`.
5. **The written report is yours.** The written report (the Day 11 decision log and the Day 12 evaluation report) is the one artifact you write by hand, from what you saw. Everything else may be AI-assisted.
6. **Be ready to explain any line.** On Day 12 we may point at one function and ask why it is written that way. "The assistant suggested it" is not an answer; "I asked it to, because …" is.

When it goes in circles: two failed fixes, then a new session and a smaller request. Keep `.env` away from it.

---

## Phases

| Phase | What to do |
|-------|------------|
| **Setup & Exploration** | Install Ollama, pull models, run benchmarks, explore the API. Complete Exercise 0 and Exercise 1. |
| **Build** | Build the RAG pipeline. Complete Exercise 2. |
| **Document & Submit** | Write your decision log, verify your test questions, push/submit your work. |

Get Ollama answering on Tuesday, while the Teams channel is staffed. Wednesday 18 November is a public holiday with nothing scheduled: an optional extra day for the build and the decision log. Questions posted in Teams that day get answered.

---

## Exercise 0: Environment Setup (30 min)

Any machine is acceptable: the company laptop or your own PC. Say which one you used in your decision log (CPU, RAM, GPU if any).

### Install Ollama (current release, 0.40.x)

| System | Install |
|---|---|
| **Windows** | The native installer, `OllamaSetup.exe` from https://ollama.com/download (Windows 10 22H2 or newer, no administrator rights). **This is the primary path.** |
| **macOS** | The app from https://ollama.com/download |
| **Linux** | `curl -fsSL https://ollama.com/install.sh \| sh` |

**Windows: install natively, not inside WSL.** WSL gets half of your RAM by default (8 GB on a 16 GB laptop), and the model has to fit in it. If you stay in WSL anyway, raise its memory: put the two lines below in `%UserProfile%\.wslconfig`, run `wsl --shutdown` in PowerShell, and reopen WSL.

```ini
[wsl2]
memory=12GB
```

Run Python on the same side as Ollama (PowerShell if Ollama is the Windows app, WSL if Ollama is inside WSL). Python inside WSL talking to Ollama on Windows may need extra network setup; we have not tested that route.

### Check that Ollama is running

```bash
ollama --version
curl http://localhost:11434/api/version
```

If the second command prints a version, the server is already running (the installers start it for you). Only if nothing answers, open a separate terminal and run `ollama serve` there. Do not start it blindly: a second server fails with an "address already in use" error.

### Pull the models

```bash
ollama pull qwen3.5:4b-q4_K_M     # main LLM for everyone, 3.3 GB download, about 4 GB of RAM
ollama pull nomic-embed-text      # embeddings, 274 MB
ollama pull qwen3.5:2b-q4_K_M     # comparison model for Exercise 1, and the fallback: 1.9 GB, about 2.3 GB of RAM
```

Optional:

```bash
ollama pull qwen3.5:9b-q4_K_M     # upgrade on a strong machine: 6.6 GB download, about 7 GB of RAM (16 GB, native Ollama)
ollama pull llama3.2:3b           # an older model with no thinking mode at all, 2.0 GB
```

Pull the tags exactly as written. The `-q4_K_M` suffix names the quantized GGUF build; on a Mac the bare tags can resolve to a larger build. You may compare any other local model as well. `llama3.2:3b` is weaker on this task (in our check it refused three questions whose answer was in the context); it is listed because it is the one model here that cannot think.

> **Memory note:** Run one LLM at a time. `ollama ps` shows what is loaded and `ollama stop <model>` frees memory. The SIZE column of `ollama ps` under-reports models that also accept images (Qwen3.5, Gemma 4): `qwen3.5:4b` shows 3.4 GB and holds about 4 GB. For real memory use, look at Task Manager / Activity Monitor / `top`.

### Raise the context window to 8192

Ollama's default context on a laptop is **4,096 tokens** (it depends on GPU memory; a machine with a large GPU gets more). Chunks, question, thinking and answer all share it. Set 8192 once, for the whole server:

| System | How |
|---|---|
| **Windows** | Add a user environment variable `OLLAMA_CONTEXT_LENGTH` = `8192` ("Edit environment variables for your account"), then quit Ollama from the tray and start it again. The context slider in the Ollama app's settings does the same. |
| **macOS** | `launchctl setenv OLLAMA_CONTEXT_LENGTH 8192`, then restart the Ollama app. |
| **Linux / WSL (service)** | `sudo systemctl edit ollama`, add `[Service]` and `Environment="OLLAMA_CONTEXT_LENGTH=8192"`, then `sudo systemctl restart ollama`. |
| **Started by hand** | `OLLAMA_CONTEXT_LENGTH=8192 ollama serve` |

The alternative travels with the model instead of the server: a Modelfile with `PARAMETER num_ctx 8192`, built with `ollama create <name> -f Modelfile` (shown in the lecture), and then `<name>` as your model. The context cannot be set per request through the OpenAI client.

### Set up Python environment

Install `uv` first if you do not have it ([installation guide](https://docs.astral.sh/uv/getting-started/installation/)), then open a new terminal so `uv` is on your PATH.

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then create the project:

```bash
mkdir local-rag
cd local-rag

uv init --python 3.12
uv add openai chromadb langchain-text-splitters pypdf
```

If you work in a Day 11 folder inside your bootcamp repository, use `uv init --python 3.12 --vcs none` so `uv` does not create a second git repository inside it. In a separate repository, plain `uv init` also creates the git repository. Either way you get a `.gitignore`, an empty `README.md` and a `main.py` you can delete. Add `chroma_db/` and `.env` to the `.gitignore`. Run your scripts with `uv run python <script>.py`. Without `uv`: Python 3.11 or newer, `python3 -m venv .venv` (on Windows `python -m venv .venv` or `py -3.12 -m venv .venv`), activate it, `pip install openai chromadb langchain-text-splitters pypdf`.

### Verify API access

Save as `test_api.py` and run `uv run python test_api.py`:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

response = client.chat.completions.create(
    model="qwen3.5:4b-q4_K_M",
    messages=[{"role": "user", "content": "Say hello in one sentence."}],
    temperature=0.3,
    reasoning_effort="none",
    max_tokens=100,
)
print(response.choices[0].message.content)
print(response.choices[0].finish_reason)
```

You should see one sentence and `stop`. Then run `ollama ps`: the CONTEXT column must read 8192.

**`reasoning_effort="none"` goes into every chat call you write.** The Qwen3.5 models think by default, thinking and answer share the `max_tokens` cap, and a model that spends the cap on thinking returns an empty answer. Remove that line from `test_api.py` once to see it happen.

### If it is too slow, or it will not run

There is no separate fallback environment. The ladder is:

1. **The smaller model.** Make `qwen3.5:2b-q4_K_M` your main model and write that down, with what you measured. It is a legitimate engineering decision, not a penalty.
2. **Another machine.** Your own PC is fine.
3. **Still stuck after 30 minutes:** say so in the Teams channel.

---

## Exercise 1: Model Comparison & Benchmarking (45–60 min)

**Goal:** Build intuition for the speed-quality-size tradeoff and produce a benchmark artifact.

### Task

Create a script `benchmark.py` that:

1. Defines a list of 5–8 test prompts spanning different capabilities:
   - A factual question
   - A reasoning/math problem
   - A summarization task (provide a paragraph to summarize)
   - A structured output request (e.g., "respond in JSON with fields: ...")
   - A code generation task
   - An instruction-following task with specific format constraints

2. Runs each prompt against at least 2 different local models (e.g., `qwen3.5:4b-q4_K_M` and `qwen3.5:2b-q4_K_M`).

3. For each model × prompt combination, records:
   - Response text
   - Tokens per second (from the API response or timing)
   - Total response time
   - `finish_reason` and whether thinking was on
   - Your own quality rating (1–5) and a short note saying why

4. Outputs results to `benchmark_results.json`.

Compare models with thinking set the same way. `completion_tokens` includes thinking tokens, so a thinking model looks several times slower and longer than the same model with thinking off.

### Skeleton

`benchmark.py`:

```python
import json
import time
from openai import OpenAI

MODELS = ["qwen3.5:4b-q4_K_M", "qwen3.5:2b-q4_K_M"]
BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"
REASONING_EFFORT = "none"

PROMPTS = [
    {"category": "factual", "prompt": "What causes tides on Earth? Answer in 2-3 sentences."},
    {"category": "reasoning", "prompt": "If a train travels 120km in 1.5 hours, and then 80km in 1 hour, what is the average speed for the entire journey?"},
    {"category": "structured", "prompt": 'List 3 European capitals. Respond ONLY with valid JSON: [{"city": ..., "country": ...}]'},
    # TODO: add more prompts
]

def run_benchmark(model: str, prompt_item: dict) -> dict:
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    start = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt_item["prompt"]}],
        temperature=0.7,
        reasoning_effort=REASONING_EFFORT,
        max_tokens=1024,
    )
    elapsed = time.time() - start
    choice = response.choices[0]
    usage = response.usage

    return {
        "model": model,
        "category": prompt_item["category"],
        "prompt": prompt_item["prompt"],
        "response": choice.message.content,
        "thinking": REASONING_EFFORT != "none",
        "finish_reason": choice.finish_reason,
        "time_seconds": round(elapsed, 2),
        "prompt_tokens": usage.prompt_tokens if usage else None,
        "completion_tokens": usage.completion_tokens if usage else None,
        "tokens_per_second": round(usage.completion_tokens / elapsed, 1) if usage and usage.completion_tokens else None,
        "quality_rating": None,
        "rating_note": "",
    }

# TODO: loop over MODELS and PROMPTS, collect results, write benchmark_results.json
# with open("benchmark_results.json", "w", encoding="utf-8").
# Print a visible warning when a response is empty.
```

After your final run, open `benchmark_results.json`, read each response, and fill in `quality_rating` (1–5) and `rating_note` by hand. Re-running the script overwrites the file, so rate last.

### Deliverable

`benchmark_results.json`: a structured file with all results, ratings filled in. You'll reference this in your decision log to justify your model choice for the RAG pipeline.

---

## Exercise 2: Local RAG Pipeline (2.5 hours)

**Goal:** Build a complete document Q&A system that runs entirely locally.

### Documents

Use the five PDFs you were given; put them in `documents/`. This is a set of internal documents from a fictional tech company. Everyone uses the same set so we can compare results after Day 12.

### Architecture Requirements

Your project must have this structure:

```
local-rag/
├── config.py          # All configuration in one place
├── ingest.py          # Document loading, chunking, embedding, storage
├── retrieve.py        # Query the vector DB, return relevant chunks
├── generate.py        # Take chunks + query, produce answer via LLM
├── pipeline.py        # End-to-end: query → retrieve → generate → answer
├── benchmark.py       # From Exercise 1
├── test_questions.json # Your Q&A test set (15-20 pairs)
├── benchmark_results.json
├── pipeline_outputs.json  # Your pipeline run over all test questions
├── decision_log.md    # Your reasoning
├── README.md          # Brief project overview, setup instructions, how to run
├── AGENTS.md          # If you use an AI assistant (rule 2)
├── documents/         # PDFs
└── chroma_db/         # Vector DB storage (gitignored, rebuilt by ingest.py)
```

`chroma_db/` is not submitted. Your README gives the one command that rebuilds it (for example `uv run python ingest.py`).

### config.py: the provider swap layer

This is architecturally important. On Day 12 you'll swap providers to compare local vs cloud.

```python
import os

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen3.5:4b-q4_K_M")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "http://localhost:11434/v1")

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
TOP_K = 5
COLLECTION_NAME = "bootcamp_docs"

SYSTEM_PROMPT = """You are a helpful assistant answering questions based on provided context.
Use ONLY the context below to answer. If the answer is not in the context, say "I cannot find this information in the provided documents."

Context:
{context}
"""
TEMPERATURE = 0.3
REASONING_EFFORT = os.getenv("REASONING_EFFORT", "none")
MAX_TOKENS = 1024
TOKEN_LIMIT_PARAM = os.getenv("TOKEN_LIMIT_PARAM", "max_tokens")
```

**`CHUNK_SIZE = 512` is characters, not tokens**, if you use `RecursiveCharacterTextSplitter` (from `langchain_text_splitters`). On these PDFs 512 characters is about 115 tokens. Whatever splitter you choose, state the unit every time you report a chunk size.

**Every chat call has the same shape:**

```python
response = client.chat.completions.create(
    model=config.LLM_MODEL,
    messages=[...],
    temperature=config.TEMPERATURE,
    reasoning_effort=config.REASONING_EFFORT,
    **{config.TOKEN_LIMIT_PARAM: config.MAX_TOKENS},
)
```

The token cap is passed under a name that comes from config because the two sides disagree on it: Ollama reads only `max_tokens`, and the Day 12 cloud model rejects `max_tokens` and wants `max_completion_tokens`. With the name in config, Day 12's swap is four environment variables and no code change:

```bash
export LLM_BASE_URL="https://<resource>.openai.azure.com/openai/v1/"   # the endpoint from your Day 8 .env
export LLM_API_KEY="$AZURE_OPENAI_API_KEY"
export LLM_MODEL="gpt-5.6-luna"
export TOKEN_LIMIT_PARAM="max_completion_tokens"
```

The same in PowerShell on Windows:

```powershell
$env:LLM_BASE_URL = "https://<resource>.openai.azure.com/openai/v1/"   # the endpoint from your Day 8 .env
$env:LLM_API_KEY = $env:AZURE_OPENAI_API_KEY
$env:LLM_MODEL = "gpt-5.6-luna"
$env:TOKEN_LIMIT_PARAM = "max_completion_tokens"
```

The Day 8 `.env` is not loaded automatically: set `AZURE_OPENAI_API_KEY` in the same shell first.

Embeddings stay local in that swap, so the same `chroma_db/` serves both runs.

### Key Implementation Notes

**For retrieval, log everything.** Your `retrieve.py` should return not just the chunks but metadata about what was retrieved:

```python
{
    "query": "What is the refund policy?",
    "retrieved_chunks": [
        {
            "content": "Refunds are processed within 30 days...",
            "source": "company_handbook.pdf",
            "page": 12,
            "relevance_score": 0.87
        },
        # ... more chunks
    ],
    "retrieval_time_ms": 45,
    "embedding_model": "nomic-embed-text"
}
```

This logged output is what Day 12's retrieval evaluation will consume.

**For generation, keep the prompt transparent.** Your `generate.py` should return the full context that was sent to the LLM alongside the answer:

```python
{
    "query": "What is the refund policy?",
    "answer": "According to the documents, refunds are processed within 30 days...",
    "context_used": "Refunds are processed within 30 days...",  # what the LLM actually saw
    "model": "qwen3.5:4b-q4_K_M",
    "thinking": False,
    "finish_reason": "stop",
    "generation_time_ms": 2340,
    "prompt_tokens": 812,
    "tokens_generated": 67
}
```

If `answer` comes back empty, print a visible warning with the `finish_reason`. An empty string saved silently is the most expensive bug of this capstone.

**For the pipeline, wire it together cleanly.** `pipeline.py`:

```python
from retrieve import retrieve_chunks
from generate import generate_answer

def answer_question(query: str) -> dict:
    retrieval_result = retrieve_chunks(query)
    generation_result = generate_answer(
        query=query,
        chunks=retrieval_result["retrieved_chunks"]
    )
    return {
        **generation_result,
        "retrieval": retrieval_result,
    }
```

### pipeline_outputs.json (required)

Run your pipeline over **all** of your test questions and save one row per question. This file is what you evaluate on Day 12, and it is where your "how many questions passed" numbers come from.

```json
[
    {
        "id": "q01",
        "question": "What is the maximum number of remote work days per week?",
        "expected_answer": "Employees may work remotely up to 3 days per week with manager approval.",
        "actual_answer": "Employees may work remotely up to 3 days per week...",
        "retrieved_context": ["chunk text 1", "chunk text 2"],
        "context_sources": [{"source": "company_handbook.pdf", "page": 12, "score": 0.87}],
        "model": "qwen3.5:4b-q4_K_M",
        "thinking": false,
        "finish_reason": "stop",
        "embedding_model": "nomic-embed-text",
        "prompt_tokens": 812,
        "tokens_generated": 67,
        "retrieval_time_ms": 45,
        "generation_time_ms": 2340,
        "passed": null,
        "rating_note": ""
    }
]
```

Your code writes `passed` as `null` and `rating_note` as `""`. After the final run, read each answer against `expected_answer` and fill both in by hand: `true` or `false`, and a short reason (for example "right number, wrong tier" or "correctly says the documents do not cover it"). Your "how many questions passed" figure is the count of `"passed": true` rows. Re-running the script overwrites the file, so rate last, as in Exercise 1.

On a laptop CPU a full run of 15–20 questions with the 4B model can take 20 minutes or more. Start it, check the first two answers, and write your decision log while it runs.

### Test Questions (15-20 pairs)

Create `test_questions.json` with questions and expected answers based on the provided documents:

```json
[
    {
        "id": "q01",
        "question": "What is the maximum number of remote work days per week?",
        "expected_answer": "Employees may work remotely up to 3 days per week with manager approval.",
        "source_document": "company_handbook.pdf",
        "difficulty": "easy",
        "type": "factual"
    },
    {
        "id": "q02",
        "question": "Compare the Professional and Enterprise support tiers.",
        "expected_answer": "Professional has support during extended business hours (06:00-22:00 CET, Monday to Friday), email support, live chat during business hours, and a 1 hour response time for critical issues. Enterprise has 24/7 support including live chat and phone, a dedicated support manager, and a 15 minute response time for critical issues.",
        "source_document": "product_guide.pdf",
        "difficulty": "medium",
        "type": "comparison"
    },
    {
        "id": "q03",
        "question": "What is the company's position on remote work for contractors?",
        "expected_answer": "The documents do not contain information about contractor remote work policies.",
        "source_document": null,
        "difficulty": "hard",
        "type": "unanswerable"
    }
]
```

**Include at least:**
- 5 easy factual questions (answer is in a single chunk)
- 5 medium questions (require synthesis from multiple chunks or documents)
- 3 hard questions (ambiguous, require reasoning, or have nuanced answers)
- 2 unanswerable questions (the answer is not in the documents; this tests hallucination resistance)

---

## Known Traps

Each of these can cost an hour. Hitting one is fine. Write down what you saw and what you did in your decision log.

| Trap | Symptom | Fix |
|---|---|---|
| **Thinking eats the token budget** | `answer` is an empty string, `finish_reason` is `"length"`, generation takes long. | Pass `reasoning_effort="none"` to `chat.completions.create`, or raise the token cap. Thinking and answer share one cap. |
| **"This model does not think"** | A model you expected to answer directly is slow and uses hundreds of extra tokens. | Every current small model we tried thinks by default in Ollama 0.40, Gemma 4 included. Set `reasoning_effort` explicitly for every model; check with `ollama show <model>`. |
| **A tag that cannot stop thinking** | You pulled `qwen3:4b` from an older tutorial. | That tag is the thinking-only build (the same files as `qwen3:4b-thinking`). Use a `qwen3.5` tag. |
| **Old advice that no longer works** | `/no_think` in the prompt or `extra_body={"think": False}` has no effect. | Qwen3.5 ignores `/no_think`; the `/v1/chat/completions` endpoint ignores `think`. Use `reasoning_effort`. |
| **Reasoning inside the answer** | With thinking off, a Granite 4.2 answer contains its reasoning and a stray `</think>`. | The model writes it into `content`, so checking the reasoning field does not catch it. Read your answers; pick another model or strip it and say so. |
| **Unfair benchmark** | One model shows 4× the tokens and time of another. | `completion_tokens` includes thinking. Compare models with thinking set the same way and record the setting. |
| **Small default context** | `ollama ps` shows CONTEXT 4096. A prompt that does not fit raises no error: the start of it is cut off (your instructions and top-ranked chunks first), and `prompt_tokens` is lower than the text you sent. | Set `OLLAMA_CONTEXT_LENGTH=8192` and restart Ollama, or build a Modelfile with `PARAMETER num_ctx 8192`. Check `ollama ps` again and log `prompt_tokens`. It cannot be set per request through the OpenAI client. |
| **Chunk size in the wrong unit** | You report "512 tokens"; your chunks are about 115 tokens. | `RecursiveCharacterTextSplitter` counts characters. State the unit. |
| **PDF tables fall apart** | Questions about numbers in tables fail; chunks contain one cell per line. | Look at your extracted text before chunking. Try `page.extract_text(extraction_mode="layout")` or another extractor, and say what you chose. |
| **Duplicate chunks after re-ingest** | The same chunk appears twice in the top-K; `collection.count()` doubles every run. | Give chunks stable IDs (source + page + index) or delete the collection before re-ingesting. Random IDs always duplicate. |
| **ChromaDB: first run crashes** | `NotFoundError: Collection [...] does not exist` on delete or get. | Catch `chromadb.errors.NotFoundError` (it is not a `ValueError`), or use `get_or_create_collection`. |
| **ChromaDB embeds behind your back** | A model download starts during `add`; later `expecting embedding with dimension of 384, got 768`. | Always pass `embeddings=` on `add` and `query_embeddings=` on `query`, from the same embedding model. |
| **Meaningless relevance scores** | Scores are negative or above 1. | Create the collection with `metadata={"hnsw:space": "cosine"}`; the default is L2 and `1 - distance` is only a similarity for cosine. |
| **Install fails on old Python** | `onnxruntime ... doesn't have a wheel for the current platform`. | Use Python 3.11 or newer: `uv init --python 3.12`. |
| **Old import path** | `ModuleNotFoundError: No module named 'langchain.text_splitter'`. | `from langchain_text_splitters import RecursiveCharacterTextSplitter` (package `langchain-text-splitters`). |
| **WSL has half your RAM** | Model loads slowly, the laptop swaps. | WSL gets 50% of RAM by default. Use the native Windows Ollama, or set `memory=12GB` under `[wsl2]` in `%UserProfile%\.wslconfig` and run `wsl --shutdown`. |
| **`ollama ps` says it is small** | SIZE shows 1–3 GB, the machine is out of memory anyway. | `ollama ps` under-reports models that also take images (Qwen3.5, Gemma 4). Check the real memory use in your system monitor. |
| **Port already in use** | `ollama serve` fails with an "address already in use" error. | Ollama is already running as a service. Skip `ollama serve`. |
| **Not actually local** | The tag has `cloud` in its name or a cloud badge in the library. | Cloud-tagged models are not allowed in this capstone. Pull a local tag. |

---

## Decision Log Template

Create `decision_log.md` using this structure. This is the one file you write by hand (rule 5).

```markdown
# Decision Log: Local RAG Pipeline

## Machine
- **Hardware:** [CPU, RAM, GPU if any; native Ollama or WSL]
- **`ollama ps` with my main model loaded:** [paste the output: name, size, processor, context]

## Model Selection
- **Chosen LLM:** [exact model tag]
- **Thinking:** [on or off, and why]
- **Why:** [Reference benchmark_results.json. What did you compare? What made you choose this one?]
- **What I considered but rejected:** [Other models and why they didn't work]

## Embedding Model
- **Chosen:** [model name, vector dimensions]
- **Why:** [Did you compare? What was the tradeoff?]

## Parsing
- **Extractor:** [which, and what one page with a table looked like after extraction]

## Chunking Strategy
- **Chunk size:** [value and unit: characters or tokens]
- **Overlap:** [value and unit]
- **Why:** [Did you experiment? What happened with different values?]

## Retrieval Configuration
- **Top-K:** [value]
- **Context window:** [value from `ollama ps`; prompt_tokens you observed at this K]
- **Why:** [Did you try different values? What was the impact?]

## Observations
- **What worked well:** [Specific examples from your test questions, with question ids from pipeline_outputs.json]
- **What failed:** [Specific examples: which questions did the system get wrong and why?]
- **Traps I hit:** [What you saw, what you did]
- **Local vs cloud expectations:** [How do you think this would compare to a cloud model on the same task?]

## If I Had More Time / Better Hardware
- [What would you change?]
```

---

## Submission

Push your work before the Day 12 session on Thursday 19 November, the same way as on the other days: a Day 11 folder in your bootcamp repository. If you prefer a separate repository for the capstone, that is fine; post its link in the Teams channel so it can be found. The folder contains:
- All Python source files (config, ingest, retrieve, generate, pipeline, benchmark)
- `benchmark_results.json` from Exercise 1, with your quality ratings filled in
- `test_questions.json` with 15-20 Q&A pairs
- `pipeline_outputs.json`: your pipeline run over all of your test questions
- `decision_log.md` with your reasoning, including the `ollama ps` output
- `README.md` with setup instructions, how to run the pipeline, the command that rebuilds `chroma_db/`, and which AI assistant you used, if any
- `AGENTS.md` if you used an assistant

Do not commit `chroma_db/`, `.venv/` or `.env`.

**The reference implementation** is shared with everyone at the start of Day 12, as a baseline for the evaluation. Day 11 points come from your own pipeline.

---

## Tips

- **Start with the simplest thing that works.** Get a basic pipeline running with default settings before optimizing. A working system with defaults scores higher than a broken system with "optimal" settings.
- **Memory matters.** The LLM, the embedding model, ChromaDB and your IDE share the same RAM. If things slow down, close the browser, check `ollama ps`, and move to the smaller model.
- **Test questions are an investment.** The quality of your test set directly affects how useful Day 12's evaluation will be. Don't rush these.
- **Document failures, not just successes.** Your decision log should show what you tried that didn't work. This is more valuable than a list of things that went smoothly.
- **Improve retrieval before you swap models.** In our check of the default settings, several expected answers were simply not in the top five chunks, for every model. Chunking and top-K move the result more than the model does.
- **Think about Day 12.** Your pipeline outputs need to be machine-readable for evaluation. Structured JSON output is required, because it is what makes automated evaluation possible.
