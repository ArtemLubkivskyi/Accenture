"""
Demo 04: Similarity matrix, with and without task prefixes
Block 4 — Run from live_materials/: uv run python code_snippets/04_embedding_similarity.py

Shows: paraphrases land close, unrelated text lands far. nomic-embed-text's
model card says every input must start with a task prefix: "search_query: "
for questions, "search_document: " for stored chunks. Ollama does not add it.
"""
import math
import sys
sys.path.insert(0, ".")
from config import get_embed_client, EMBED_BASE_URL, EMBED_MODEL

client = get_embed_client()

QUERY = "How many days a week can I work from home?"
DOCUMENTS = {
    "remote":     "Employees may work remotely up to three days per week with manager approval.",
    "paraphrase": "With their manager's agreement, staff can work from home at most three days each week.",
    "budget":     "Each employee receives a learning budget of 2,000 euros per year.",
    "recipe":     "The recipe needs two eggs, a cup of flour and a pinch of salt.",
}


def cosine_sim(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b)


def embed(texts):
    response = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in response.data]


def print_matrix(title, query_prefix, doc_prefix):
    labels = ["query"] + list(DOCUMENTS)
    texts = [query_prefix + QUERY] + [doc_prefix + d for d in DOCUMENTS.values()]
    vecs = embed(texts)

    print(f"=== {title} ===")
    print(f"First input sent: \"{texts[0]}\"\n")
    print(" " * 12 + "".join(f"{label:>12}" for label in labels))
    for label, row in zip(labels, vecs):
        print(f"{label:<12}" + "".join(f"{cosine_sim(row, col):>12.3f}" for col in vecs))
    print()
    return {label: cosine_sim(vecs[0], v) for label, v in zip(labels[1:], vecs[1:])}


print(f"Endpoint: {EMBED_BASE_URL}")
print(f"Model:    {EMBED_MODEL}\n")

plain = print_matrix("Without prefixes", "", "")
prefixed = print_matrix("With prefixes", "search_query: ", "search_document: ")

print("=== Query against each document ===")
print(f"{'document':<12}{'plain':>8}{'prefixed':>10}")
for label in DOCUMENTS:
    print(f"{label:<12}{plain[label]:>8.3f}{prefixed[label]:>10.3f}")

print(f"\nRanking, plain:     {' > '.join(sorted(plain, key=plain.get, reverse=True))}")
print(f"Ranking, prefixed:  {' > '.join(sorted(prefixed, key=prefixed.get, reverse=True))}")
print("\n→ Retrieval uses the ranking, not the raw score. Compare scores only within one setting.")
print("→ The model card asks for prefixes: add them in ingest.py and retrieve.py, both or neither.")
