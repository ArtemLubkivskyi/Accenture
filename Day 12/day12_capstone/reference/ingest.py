"""Document ingestion: load PDFs, chunk, embed, and store in ChromaDB."""

import os
import hashlib

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from pypdf import PdfReader

import config


def load_documents(documents_dir: str = config.DOCUMENTS_DIR) -> list[dict]:
    documents = []
    for filename in sorted(os.listdir(documents_dir)):
        if not filename.lower().endswith(".pdf"):
            continue
        filepath = os.path.join(documents_dir, filename)
        for page_number, page in enumerate(PdfReader(filepath).pages, start=1):
            documents.append({
                "content": page.extract_text(),
                "source": filename,
                "page": page_number,
            })
    print(f"Loaded {len(documents)} pages from {documents_dir}")
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for doc in documents:
        splits = splitter.split_text(doc["content"])
        for i, text in enumerate(splits):
            chunk_id = hashlib.md5(
                f"{doc['source']}:{doc['page']}:{i}".encode()
            ).hexdigest()
            chunks.append({
                "id": chunk_id,
                "content": text,
                "source": doc["source"],
                "page": doc["page"],
                "chunk_index": i,
            })
    print(f"Created {len(chunks)} chunks (size={config.CHUNK_SIZE} characters, overlap={config.CHUNK_OVERLAP})")
    return chunks


def embed_and_store(chunks: list[dict]) -> chromadb.Collection:
    """Recreates the collection on every run, so re-ingesting never duplicates chunks."""
    client = OpenAI(base_url=config.EMBEDDING_BASE_URL, api_key=config.EMBEDDING_API_KEY)
    chroma_client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)

    try:
        chroma_client.delete_collection(config.COLLECTION_NAME)
    except chromadb.errors.NotFoundError:
        pass
    collection = chroma_client.create_collection(
        name=config.COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    batch_size = 20
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        texts = [c["content"] for c in batch]

        response = client.embeddings.create(
            model=config.EMBEDDING_MODEL,
            input=texts,
        )
        embeddings = [item.embedding for item in response.data]

        collection.add(
            ids=[c["id"] for c in batch],
            documents=texts,
            embeddings=embeddings,
            metadatas=[
                {"source": c["source"], "page": c["page"], "chunk_index": c["chunk_index"]}
                for c in batch
            ],
        )
        print(f"  Embedded batch {i // batch_size + 1}/{(len(chunks) - 1) // batch_size + 1}")

    print(f"Stored {collection.count()} chunks in ChromaDB at {config.CHROMA_PERSIST_DIR}")
    return collection


def ingest(documents_dir: str = config.DOCUMENTS_DIR) -> chromadb.Collection:
    documents = load_documents(documents_dir)
    chunks = chunk_documents(documents)
    collection = embed_and_store(chunks)
    return collection


if __name__ == "__main__":
    ingest()
