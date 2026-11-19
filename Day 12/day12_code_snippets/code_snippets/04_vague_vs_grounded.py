"""Demo 04, Block 2 slide "Vague prompt vs grounded rubric".

The same two answers through two judge prompts. Answer B is longer and has one invented sentence.
A vague "rate the quality" prompt may let it through; a rubric that checks every claim against
the context catches it. Current judges sometimes catch it with the vague prompt too: say so if they do.

    uv run python code_snippets/04_vague_vs_grounded.py
"""

import json

from _common import JUDGE_MODEL, foundry_client, rule

client = foundry_client()

QUESTION = "What is the company's remote work policy?"
CONTEXT = "Employees may work remotely up to 3 days per week with manager approval."
ANSWERS = {
    "A (correct, concise)": "Employees may work remotely up to 3 days per week with manager approval.",
    "B (padded, one invented detail)": (
        "The company has implemented a flexible remote work program designed to support work-life balance. "
        "Under this policy, employees are permitted to work from home up to 3 days per week, subject to "
        "approval from their direct line manager. Additionally, employees in senior positions may be eligible "
        "for more flexible arrangements depending on their role requirements."
    ),
}

VAGUE = """Rate the quality of this answer from 1 to 5.

QUESTION: {question}
ANSWER: {answer}

Respond with JSON: {{"score": <1-5>, "reason": "<one sentence>"}}"""

GROUNDED = """Check every claim in the answer against the context.

RUBRIC:
  5 = Every claim is supported by the context
  3 = One minor claim is not in the context
  1 = A claim contradicts the context or adds a fact the context does not contain
Length and tone do not count.

QUESTION: {question}
CONTEXT: {context}
ANSWER: {answer}

Respond with JSON: {{"score": <1-5>, "reason": "<one sentence>"}}"""


def score(template: str, answer: str) -> dict:
    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": template.format(question=QUESTION, context=CONTEXT, answer=answer)}],
        response_format={"type": "json_object"},
        reasoning_effort="low",
    )
    return json.loads(response.choices[0].message.content)


for prompt_name, template in [("Vague prompt: rate the quality 1-5", VAGUE),
                              ("Grounded rubric: check every claim", GROUNDED)]:
    rule(prompt_name)
    for label, answer in ANSWERS.items():
        verdict = score(template, answer)
        print(f"{label:<34} {verdict['score']}/5  {verdict['reason']}")

rule()
print(f"Judge: {JUDGE_MODEL}. 'Senior positions may be eligible' is not in the context.")
