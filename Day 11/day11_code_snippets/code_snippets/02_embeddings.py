"""
Demo 02: Local embeddings with nomic-embed-text
Block 4 — Run from live_materials/: python code_snippets/02_embeddings.py

Shows: Same OpenAI SDK for embeddings. Zero cost per call.

Endpoint and model come from config.py (default: Ollama on localhost:11434).
To run against another Ollama server:
  export EMBED_BASE_URL=http://<host>:11434/v1
"""
import math
import sys
sys.path.insert(0, ".")
from config import get_embed_client, EMBED_BASE_URL, EMBED_MODEL

client = get_embed_client()

texts = [
    "Quantization reduces model size by using fewer bits per weight.",
    "The capital of France is Paris.",
    "Quantized models use INT4 or INT8 instead of FP32.",
]

print("=== Embedding Demo ===")
print(f"Endpoint: {EMBED_BASE_URL}")
print(f"Model:    {EMBED_MODEL}\n")

response = client.embeddings.create(model=EMBED_MODEL, input=texts)
vecs = [item.embedding for item in response.data]

for text, vector in zip(texts, vecs):
    print(f"Text:       \"{text[:60]}...\"")
    print(f"Dimensions: {len(vector)}")
    print(f"First 5:    {[round(v, 4) for v in vector[:5]]}")
    print()


def cosine_sim(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b)


print("=== Similarity Demo ===\n")
print(f"Sim(quantization, Paris):        {cosine_sim(vecs[0], vecs[1]):.4f}")
print(f"Sim(quantization, INT4/INT8):    {cosine_sim(vecs[0], vecs[2]):.4f}")
print("\n→ Related texts have higher similarity. This is how RAG retrieval works.")
