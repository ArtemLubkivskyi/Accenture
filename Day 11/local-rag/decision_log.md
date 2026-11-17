# Decision Log: Local RAG Pipeline

## Machine
- **Hardware:** company laptop, Intel Core i5-10310U, 16 GB RAM, Intel UHD Graphics (no usable GPU). Native Windows Ollama 0.40.16, not WSL. Everything runs on the CPU.
- **`ollama ps` with my main model loaded:**

```
NAME                       ID              SIZE      PROCESSOR    CONTEXT    RUNNER      UNTIL
qwen3.5:4b-q4_K_M          d8b0f5e9760c    3.4 GB    100% CPU     8192       llamacpp    4 minutes from now
nomic-embed-text:latest    0a109f422b47    389 MB    100% CPU     2048       llamacpp    4 minutes from now
```

## Model Selection
- **Chosen LLM:** `qwen3.5:4b-q4_K_M`
- **Thinking:** off (`reasoning_effort="none"`) for both models. On CPU thinking would make every answer much slower, and thinking tokens share the token cap with the answer, so it can come back empty. With thinking off all 19 pipeline answers ended with `finish_reason: stop` and none was empty (`pipeline_outputs.json`).
- **Why:** I compared the 4b and 2b models on 7 prompts each, same settings (`benchmark_results.json`). Numbers from `summarize.py`:

  | model | avg time | avg tok/s | avg rating (1-5) |
  |---|---|---|---|
  | qwen3.5:4b-q4_K_M | 20.1 s | 4.8 | 4.57 |
  | qwen3.5:2b-q4_K_M | 11.2 s | 11.0 | 3.71 |

  The 2b model is about twice as fast, but it made real mistakes: the summary had a wrong fact and the code had a bug (it is not case-insensitive). For a Q&A system that must be correct, I prefer slower and right. One warm-up call per model is done before measuring, so loading time is not counted.
- **What I considered but rejected:** `qwen3.5:2b-q4_K_M` (faster but less accurate, see above). I did not try the 9b model because with 16 GB RAM and no GPU it would be too slow.

## Embedding Model
- **Chosen:** `nomic-embed-text`, 768 dimensions (printed by `ingest.py`).
- **Why:** it is the local model from the course and small (274 MB). I did not compare other embedding models. I add the `search_document: ` and `search_query: ` prefixes because the model card asks for them (shown in the lecture demo 04).

## Parsing
- **Extractor:** `pypdf`, `extract_text()` in plain mode. I compared plain and layout mode on a table page with `peek_pdf.py product_guide.pdf 14`. Plain mode keeps each table row on one line, for example `Critical (service down) 4 hours 1 hour 15 minutes`. Layout mode gives the same rows but with a lot of spaces, which wastes space in a 512 character chunk. Tables with cells that wrap over several lines (like the office table in the handbook) still come out a bit broken in plain mode. I also remove the empty list markers (`•`, `1.`) that pypdf puts at the end of each page.

## Chunking Strategy
- **Chunk size:** 512 characters (not tokens), `RecursiveCharacterTextSplitter`.
- **Overlap:** 50 characters.
- **Why:** I kept the default to get a working pipeline first. I split each page separately so every chunk has the correct page number. 85 pages gave 330 chunks, average 427 characters (printed by `ingest.py`). Chunk IDs are `file-page-index`, and the collection is deleted before re-ingest, so running `ingest.py` twice still gives 330 chunks. I did not try other chunk sizes yet.

## Retrieval Configuration
- **Top-K:** 5
- **Context window:** 8192 (from `ollama ps`). Prompt tokens were 604 to 862, average 723 (`pipeline_outputs.json`), so the context is far from full and nothing is cut off.
- **Why:** default value. The expected page was in the top 5 for 14 of 17 questions that have a source page (`summarize.py`, using the `evidence` field in `test_questions.json`). One small experiment: for q06 the right page (meeting notes p5) was missing at top-5. With top-10 it shows up at rank 7 (`experiment_q06_topk10.txt`). Since the context is only around 700 tokens, a bigger top-k would fit easily, but I did not re-run the whole test set with it.

## Observations
- **What worked well:** 16 of 19 questions passed (`pipeline_outputs.json`, `passed` field). Simple facts were right (q01 to q05). It also handled a table calculation (q16, 10% credit) and the three unanswerable questions (q17, q18, q19) without making things up. For q12 and q13 it noticed that the meeting notes changed the handbook rule.
- **What failed:**
  - q06: answered Salesforce instead of HubSpot. Retrieval only found the January meeting where Salesforce was recommended, not the February decision. A retrieval problem, not a model problem.
  - q15: gave only the January 15 date from the quarterly report and ignored that the meeting notes say April, even though both pages were in the context. The model does not point out conflicts by itself.
  - q08: right price but did not calculate the saving in euro.
- **Traps I hit:** none of the bad ones, because I followed the brief from the start (reasoning off, context 8192, cosine space, stable IDs, passing my own embeddings). The main issue was speed: about 52 s per answer on average, up to 139 s for q07 (`pipeline_outputs.json`), so the full run took around 17 minutes.
- **Local vs cloud expectations:** I expect a cloud model to be much faster and better at the hard questions, for example noticing conflicts like q15 and doing the calculation in q08. It would not fix q06, because the problem there is retrieval. The local setup is slow, but no document leaves the laptop, which is the main requirement of the client.

## If I Had More Time / Better Hardware
- Re-run the test set with top-k 8 or 10 and check if q06 is fixed.
- Add a line to the prompt asking the model to mention when documents disagree (q15).
- Try bigger chunks (e.g. 1000 characters) so tables stay together.
- With a GPU, try `qwen3.5:9b` and compare it on the same test questions.
