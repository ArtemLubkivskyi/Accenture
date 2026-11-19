"""Demo 06, Block 3 slides "The unanswerable question test" and "Demo: same question, three contexts".

Four (context, answer) pairs scored by DeepEval with FaithfulnessMetric twice, with the default
settings and with penalize_ambiguous_claims=True, plus AnswerRelevancy:
  accurate     the answer matches the context
  outdated     the answer contradicts the context
  partial      the answer adds a date the context does not have
  unanswerable the answer invents a contractor policy the documents never mention
By default only contradictions fail; a claim the context does not mention counts as supported.

    uv run python code_snippets/06_faithfulness_cases.py
    uv run python code_snippets/06_faithfulness_cases.py --generate   # local model writes the answers
"""

import sys

from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase

from _common import JUDGE_MODEL, RAG_SYSTEM_PROMPT, chat, deepeval_judge, rule

CASES = [
    ("accurate", "When was the remote work policy last updated?",
     "Remote Work Policy: employees may work remotely up to 3 days per week. Policy updated January 15, 2024.",
     "The policy was last updated on January 15, 2024."),
    ("outdated", "When was the remote work policy last updated?",
     "Remote Work Policy: employees may work remotely up to 3 days per week. Policy updated January 15, 2024.",
     "The policy was last updated on January 15, 2025."),
    ("partial", "When was the remote work policy last updated?",
     "Remote Work Policy: employees may work remotely up to 3 days per week with manager approval.",
     "The remote work policy was last updated on January 15, 2024."),
    ("unanswerable", "What is the company's policy on contractor remote work?",
     "Remote Work Policy: full-time employees may work remotely up to 3 days per week with manager approval.",
     "Contractors may work remotely following the same policies as full-time employees."),
]

judge = deepeval_judge()
generate = "--generate" in sys.argv

rows = []
for label, question, context, answer in CASES:
    if generate:
        answer = chat([{"role": "system", "content": RAG_SYSTEM_PROMPT.format(context=context)},
                       {"role": "user", "content": question}], target="local", max_tokens=256)["text"]
    case = LLMTestCase(input=question, actual_output=answer, retrieval_context=[context])
    scores = {}
    for name, metric in [
        ("faith_default", FaithfulnessMetric(threshold=0.7, model=judge, async_mode=False)),
        ("faith_penalize", FaithfulnessMetric(threshold=0.7, model=judge, async_mode=False,
                                              penalize_ambiguous_claims=True)),
        ("relevancy", AnswerRelevancyMetric(threshold=0.7, model=judge, async_mode=False)),
    ]:
        metric.measure(case)
        scores[name] = metric.score
    refused = "cannot find this information" in answer.lower()
    rows.append((label, answer, scores, refused))
    rule(label)
    print(f"Context: {context}\nAnswer:  {answer}")
    print(f"Faithfulness default {scores['faith_default']:.2f} · with penalize_ambiguous_claims "
          f"{scores['faith_penalize']:.2f} · AnswerRelevancy {scores['relevancy']:.2f} · refusal {refused}")

rule(f"Summary, judge {JUDGE_MODEL}")
print(f"{'case':<14} {'Faith default':>14} {'Faith penalize':>15} {'AnswerRel':>10}")
for label, _, s, _ in rows:
    print(f"{label:<14} {s['faith_default']:>14.2f} {s['faith_penalize']:>15.2f} {s['relevancy']:>10.2f}")
print("\nIf 'partial' and 'unanswerable' drop only with the flag, keep the flag in eval_pipeline.py.")
