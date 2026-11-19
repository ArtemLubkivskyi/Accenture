"""Demo 05, Block 2 slide 'Demo: "I don't know" vs fabrication'.

A question whose answer is not in the context, asked with two system prompts. The second adds one
sentence: if the answer is not in the context, say so. The answer is then checked for the refusal
sentence, the check that needs no judge.

    uv run python code_snippets/05_idk_vs_fabrication.py           # local model (Ollama), the students' setup
    uv run python code_snippets/05_idk_vs_fabrication.py --cloud   # gpt-5.6-luna on Foundry
"""

import sys

from _common import REFUSAL, chat, rule

TARGET = "cloud" if "--cloud" in sys.argv else "local"

CONTEXT = """Remote Work Policy (updated January 15, 2024):
Full-time employees may work remotely up to 3 days per week with manager approval.
Employees must be available during core hours (10:00-15:00) on remote days.
Equipment provided: laptop, monitor, keyboard. Internet costs are not reimbursed."""

QUESTION = "What is the company's policy on remote work for contractors?"

PROMPTS = {
    "Default system prompt": "You are a helpful assistant answering questions based on provided context.\n\nContext:\n{context}",
    "Calibrated system prompt": (
        "You are a helpful assistant answering questions based on provided context.\n"
        f'Use ONLY the context below to answer. If the answer is not in the context, say "{REFUSAL}"\n\n'
        "Context:\n{context}"
    ),
}

print(f"Question: {QUESTION}\nThe context says nothing about contractors.")
for label, system in PROMPTS.items():
    rule(label)
    r = chat([{"role": "system", "content": system.format(context=CONTEXT)},
              {"role": "user", "content": QUESTION}], target=TARGET, max_tokens=512)
    print(r["text"])
    refused = "cannot find this information" in r["text"].lower()
    print(f"\nRefusal sentence present: {refused}   ({r['model']}, {r['seconds']} s)")

rule()
print("Most benchmarks give 'I don't know' zero points, the same as a wrong answer (Kalai et al., 2025),")
print("so models learn to guess. The instruction makes a refusal reliable, and the string check makes it measurable.")
