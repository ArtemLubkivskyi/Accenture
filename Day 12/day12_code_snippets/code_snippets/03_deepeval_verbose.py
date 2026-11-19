"""Demo 03, Block 2 slide "Live demo: a judge from scratch", second part: read what the judge does.

One case through DeepEval's FaithfulnessMetric with verbose_mode=True: the claims it extracted,
the truths from the context and the verdict per claim. Then where DeepEval keeps its prompts.

    uv run python code_snippets/03_deepeval_verbose.py
"""

from pathlib import Path

import deepeval.templates
from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase

from _common import JUDGE_MODEL, deepeval_judge, rule

case = LLMTestCase(
    input="What is the remote work policy?",
    actual_output=("Employees can work remotely up to 3 days per week with manager approval. "
                   "Senior employees in director-level positions may qualify for fully remote arrangements."),
    retrieval_context=["Employees may work remotely up to 3 days per week with manager approval. "
                       "The policy was updated on January 15, 2024."],
)

rule(f"FaithfulnessMetric, judge {JUDGE_MODEL}, verbose_mode=True")
metric = FaithfulnessMetric(threshold=0.7, model=deepeval_judge(), verbose_mode=True, async_mode=False)
metric.measure(case)

rule("Result")
print(f"Score:  {metric.score}")
print(f"Reason: {metric.reason}")
print(f"Cost:   {metric.evaluation_cost}")
prompts = Path(deepeval.templates.__file__).parent / "metrics"
print(f"\nThe prompts DeepEval sends to the judge: {prompts / 'templates.json'} (shared parts in {prompts / 'fragments'})")
