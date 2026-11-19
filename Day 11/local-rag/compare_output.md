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
