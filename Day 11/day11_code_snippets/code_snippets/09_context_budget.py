"""
Demo 09: Context budget and the silent cut
Block 7 — Run from live_materials/: uv run python code_snippets/09_context_budget.py

Shows: a RAG prompt with k chunks of 512 characters, the estimate
(characters / 4.4) against usage.prompt_tokens from the server, and what
happens once the prompt is longer than the context: no error, prompt_tokens
stops growing, and the start of the prompt (system instruction and the
top-ranked chunk) is gone. CONTEXT_LENGTH must match the server's setting.
"""
import sys
sys.path.insert(0, ".")
from config import get_llm_client, CONTEXT_LENGTH, LLM_BASE_URL, LLM_MODEL, TOKEN_LIMIT_PARAM

client = get_llm_client()

SYSTEM = (
    "Answer ONLY from the context. If the answer is not in the context, say "
    "'I cannot find this information in the provided documents.'\n\nContext:\n"
)
QUESTION = "What is the name of the office plant on floor 3?"
TOP_CHUNK = "The office plant on floor 3 is a ficus called Gerald. It is watered on Mondays."
ANSWER_ROOM = 100
CHARS_PER_TOKEN = 4.4


def filler_chunk(i):
    sentence = (
        f"Section {i}: meeting room {i} seats {4 + i % 9} people and is booked through the "
        f"facilities portal. Projector cable type {i % 3 + 1} is kept in the drawer. "
    )
    return (sentence * 8)[:512]


def build_messages(k):
    chunks = [TOP_CHUNK] + [filler_chunk(i) for i in range(1, k)]
    context = "\n\n".join(f"[{n + 1}] {c}" for n, c in enumerate(chunks))
    return [
        {"role": "system", "content": SYSTEM + context},
        {"role": "user", "content": QUESTION},
    ]


print(f"Endpoint: {LLM_BASE_URL}")
print(f"Model:    {LLM_MODEL}")
print(f"Context:  {CONTEXT_LENGTH} tokens (from config; check `ollama ps`)")
print(f"Question: {QUESTION}  (answer is in chunk 1)\n")
print(f"{'k':>4} {'estimate':>9} {'prompt_tokens':>14} {'fits (est.)':>12}  answer")

for k in [5, 20, 50, 65, 80]:
    messages = build_messages(k)
    chars = sum(len(m["content"]) for m in messages)
    estimate = round(chars / CHARS_PER_TOKEN)
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.0,
        reasoning_effort="none",
        **{TOKEN_LIMIT_PARAM: ANSWER_ROOM},
    )
    fits = "yes" if estimate + ANSWER_ROOM <= CONTEXT_LENGTH else "NO"
    answer = response.choices[0].message.content.strip().replace("\n", " ")
    print(f"{k:>4} {estimate:>9} {response.usage.prompt_tokens:>14} {fits:>12}  {answer[:60]}")

print("\n→ Past the limit there is no error: the start of the prompt is dropped and prompt_tokens falls.")
print("→ characters / 4.4 is an estimate. Log prompt_tokens in every row of pipeline_outputs.json.")
