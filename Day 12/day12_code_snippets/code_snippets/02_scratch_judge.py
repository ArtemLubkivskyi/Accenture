"""Demo 02, Block 2 slide "Live demo: a judge from scratch".

A judge is a prompt with a rubric, sent to a stronger model. Three answers against the same context:
faithful, adds facts that are not in the context, contradicts the context.

    uv run python code_snippets/02_scratch_judge.py
"""

import json

from _common import JUDGE_MODEL, foundry_client, rule

client = foundry_client()

JUDGE_PROMPT = """You are evaluating an answer from a RAG system.

CRITERIA: Faithfulness. Does the answer contain only claims supported by the context?
RUBRIC:
  5 = Every claim directly supported by the context
  3 = Most claims supported, 1-2 minor unsupported claims
  1 = Answer contains claims that contradict the context or are not in it

QUESTION: {question}
CONTEXT: {context}
ANSWER: {answer}

Respond with JSON: {{"score": <1-5>, "reason": "<one sentence>"}}"""

CONTEXT = ("Employees may work remotely up to 3 days per week with manager approval. "
           "The policy was updated on January 15, 2024.")

CASES = [
    ("faithful", "What is the remote work policy?",
     "Employees can work remotely up to 3 days per week, subject to manager approval."),
    ("adds facts not in the context", "What is the remote work policy?",
     "Employees can work remotely up to 3 days per week with manager approval. "
     "Senior employees in director-level positions may qualify for fully remote arrangements."),
    ("contradicts the context", "When was the remote work policy updated?",
     "The remote work policy was updated on January 15, 2025."),
]


def judge_faithfulness(question: str, answer: str, context: str) -> dict:
    prompt = JUDGE_PROMPT.format(question=question, context=context, answer=answer)
    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        reasoning_effort="low",
    )
    return json.loads(response.choices[0].message.content)


for i, (label, question, answer) in enumerate(CASES, 1):
    rule(f"Case {i}: {label}")
    print(f"Answer: {answer}")
    verdict = judge_faithfulness(question, answer, CONTEXT)
    print(f"Score:  {verdict['score']}/5")
    print(f"Reason: {verdict['reason']}")

rule()
print(f"Judge: {JUDGE_MODEL}. DeepEval's FaithfulnessMetric does the same per claim, with retries.")
