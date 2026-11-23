# Evaluation Report: Local RAG Pipeline

## Run details
Pipeline: [your own / the reference]. Local model: [tag], thinking [on/off].
Cloud model: gpt-5.6-luna. Judge: gpt-5.4-mini, DeepEval [version].
Test set: [n] questions, [n] unanswerable. Date of the runs.

## Executive summary
After 19 control questions, our RAG pipeline showed basic functionality, but I think that it is not ready for production in its current state. I recommend keeping the system local, as the client requires, but moving it to GPU hardware: quality matched the cloud model, and the latency gap is mainly a hardware problem (expected to shrink a lot on a GPU, still to be measured). The system rejects questions that have no answers in the knowledge base (3 out of 3 refusals without hallucinations). However, the information retrieval quality is limited by top 5 search window (Contextual Recall is 0.74 +- 0.18 with Hit at 5 equal to 1.00). The retriever finds the right PDF document but it has some problems with specific passages(It just misses them). For example, the latest decision to switch to HubSpot in q06 was only ranked seventh. In addition, the evaluation framework underestimates generation quality (Faithfulness is 0.74 +- 0.11) because the evaluation script does not pass page metadata to the judge, so correct model citations are treated as fabricated.

## Retrieval quality  (source: eval_results_local.json)
- ContextualRelevancy, ContextualRecall, ContextualPrecision: mean ± 2×SE each
- Which questions retrieve badly, and why: chunking, embedding, top-K?

## Generation quality  (source: eval_results_local.json)
- Faithfulness, AnswerRelevancy: mean ± 2×SE
- Unanswerable questions: [x of n] refused correctly
- Empty or failed answers: [n], and why
- Where the judge and your own ratings disagree, and who was right

## Local vs cloud  (source: compare.py output)

| Metric | n | Local | Cloud | Cloud - Local | Verdict |
|---|---|---|---|---|---|
| Faithfulness | 19 | 0.74 ± 0.11 | 0.68 ± 0.22 | -0.05 ± 0.21 | no clear difference |
| Answer Relevancy | 19 | 0.90 ± 0.08 | 0.97 ± 0.05 | +0.07 ± 0.08 | no clear difference |
| Contextual Relevancy | 19 | 0.28 ± 0.09 | 0.30 ± 0.11 | +0.02 ± 0.06 | no clear difference |
| Contextual Recall | 19 | 0.74 ± 0.18 | 0.68 ± 0.19 | -0.05 ± 0.13 | no clear difference |
| Contextual Precision | 19 | 0.83 ± 0.12 | 0.80 ± 0.12 | -0.03 ± 0.04 | no clear difference |

Questions where cloud and local differ by 0.3 or more:
- Faithfulness: q01 (+0.50), q02 (-0.33), q03 (+0.50), q06 (-1.00), q10 (+0.50), q11 (+0.40), q12 (+0.33), q16 (-0.67), q17 (-0.50), q18 (-0.75), q19 (-0.40)
- Answer Relevancy: q17 (+0.60)
- Contextual Relevancy: q07 (+0.41)
- Contextual Recall: q05 (-1.00), q13 (+0.50), q15 (-0.50)
- Contextual Precision: q01 (-0.30)

| Run | Model | Median generation | Slowest | Avg completion tokens | Empty or failed |
|---|---|---|---|---|---|
| local | qwen3.5:4b-q4_K_M | 48.6 s | 139.0 s (q07) | 119 | 0 |
| cloud | gpt-5.6-luna | 1.1 s | 1.5 s (q07) | 39 | 0 |

Completion tokens come from usage.completion_tokens, which includes reasoning tokens when reported.

[what it means, with question ids]

## Security assessment  (source: security_results_*.json)
| Attack | Local | Cloud |
|---|---|---|
| [your verdicts, including your own attacks] | | |

What a production deployment would need.

## Recommendations
1. [the most important fix, specific]
2. [the next one]
3. [what you would test next]

## Limitations
[sample size, one judge, what you did not test]
