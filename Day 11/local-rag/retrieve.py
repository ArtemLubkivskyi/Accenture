"""Query the vector DB and return the top chunks with scores.

uv run python retrieve.py "How many PTO days do employees get?"
"""
import sys
import time

import chromadb
from openai import OpenAI

import config

embed_client = OpenAI(base_url=config.EMBEDDING_BASE_URL, api_key=config.EMBEDDING_API_KEY)
_collection = None


def get_collection():
    global _collection
    if _collection is None:
        db = chromadb.PersistentClient(path=config.CHROMA_DIR)
        _collection = db.get_collection(config.COLLECTION_NAME)
    return _collection


def retrieve_chunks(query, top_k=None):
    top_k = top_k or config.TOP_K
    start = time.time()

    vec = embed_client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input=[config.QUERY_PREFIX + query],
    ).data[0].embedding

    res = get_collection().query(query_embeddings=[vec], n_results=top_k)

    chunks = []
    for text, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        chunks.append({
            "content": text,
            "source": meta["source"],
            "page": meta["page"],
            "relevance_score": round(1 - dist, 4),  # cosine similarity
        })

    return {
        "query": query,
        "retrieved_chunks": chunks,
        "retrieval_time_ms": round((time.time() - start) * 1000),
        "embedding_model": config.EMBEDDING_MODEL,
        "top_k": top_k,
    }


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "How many PTO days do employees get?"
    result = retrieve_chunks(q)
    print(f"Query: {q}  ({result['retrieval_time_ms']} ms)\n")
    for i, c in enumerate(result["retrieved_chunks"], 1):
        print(f"[{i}] {c['source']} p.{c['page']}  score={c['relevance_score']}")
        print("    " + c["content"][:300].replace("\n", " ") + "\n")
