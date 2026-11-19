"""Retrieval: query the vector DB and return relevant chunks with metadata."""

import time

import chromadb
from openai import OpenAI

import config


def get_collection() -> chromadb.Collection:
    chroma_client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
    return chroma_client.get_collection(name=config.COLLECTION_NAME)


def retrieve_chunks(query: str, top_k: int = config.TOP_K) -> dict:
    """Returns the chunks in rank order with source, page and cosine similarity."""
    start = time.time()

    client = OpenAI(base_url=config.EMBEDDING_BASE_URL, api_key=config.EMBEDDING_API_KEY)
    response = client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input=[query],
    )
    query_embedding = response.data[0].embedding

    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    elapsed_ms = round((time.time() - start) * 1000)

    retrieved_chunks = []
    for i in range(len(results["ids"][0])):
        retrieved_chunks.append({
            "content": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "page": results["metadatas"][0][i]["page"],
            "relevance_score": round(1 - results["distances"][0][i], 4),
        })

    return {
        "query": query,
        "retrieved_chunks": retrieved_chunks,
        "retrieval_time_ms": elapsed_ms,
        "top_k": top_k,
        "embedding_model": config.EMBEDDING_MODEL,
    }


if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "What is the remote work policy?"
    result = retrieve_chunks(query)
    print(f"Query: {result['query']}")
    print(f"Retrieved {len(result['retrieved_chunks'])} chunks in {result['retrieval_time_ms']}ms\n")
    for i, chunk in enumerate(result["retrieved_chunks"]):
        print(f"--- Chunk {i+1} (score: {chunk['relevance_score']}, source: {chunk['source']} p.{chunk['page']}) ---")
        print(chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"])
        print()
