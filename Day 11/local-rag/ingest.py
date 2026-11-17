"""Load PDFs, chunk them, embed with nomic-embed-text, store in ChromaDB.

Rebuilds chroma_db/ from scratch every run:
uv run python ingest.py
"""
import re
import time
from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from pypdf import PdfReader

import config

embed_client = OpenAI(base_url=config.EMBEDDING_BASE_URL, api_key=config.EMBEDDING_API_KEY)


def clean_page(text):
    # pypdf puts list markers ("1.", "•") on their own lines at the end of a page, drop them
    lines = [ln.rstrip() for ln in text.splitlines()]
    lines = [ln for ln in lines if not re.fullmatch(r"\s*(•|\d+\.)\s*", ln)]
    return "\n".join(lines).strip()


def load_pages():
    pages = []
    for pdf in sorted(Path(config.DOCS_DIR).glob("*.pdf")):
        reader = PdfReader(pdf)
        for i, page in enumerate(reader.pages, start=1):
            text = clean_page(page.extract_text(extraction_mode=config.PDF_EXTRACTION_MODE))
            if text:
                pages.append({"source": pdf.name, "page": i, "text": text})
        print(f"  {pdf.name}: {len(reader.pages)} pages")
    return pages


def make_chunks(pages):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    chunks = []
    # split page by page so every chunk keeps its real page number
    for p in pages:
        for j, piece in enumerate(splitter.split_text(p["text"])):
            chunks.append({
                "id": f"{p['source']}-p{p['page']}-c{j}",  # stable id, no duplicates on re-run
                "text": piece,
                "source": p["source"],
                "page": p["page"],
            })
    return chunks


def embed_texts(texts, prefix, batch_size=32):
    vectors = []
    for i in range(0, len(texts), batch_size):
        batch = [prefix + t for t in texts[i:i + batch_size]]
        resp = embed_client.embeddings.create(model=config.EMBEDDING_MODEL, input=batch)
        vectors.extend(item.embedding for item in resp.data)
    return vectors


def main():
    start = time.time()
    print("Loading PDFs...")
    pages = load_pages()
    chunks = make_chunks(pages)
    sizes = [len(c["text"]) for c in chunks]
    print(f"{len(pages)} pages -> {len(chunks)} chunks "
          f"(chunk_size={config.CHUNK_SIZE} chars, overlap={config.CHUNK_OVERLAP} chars, "
          f"avg {sum(sizes) / len(sizes):.0f} chars)")

    print(f"Embedding with {config.EMBEDDING_MODEL}...")
    vectors = embed_texts([c["text"] for c in chunks], config.DOC_PREFIX)
    print(f"  vector size: {len(vectors[0])}")

    db = chromadb.PersistentClient(path=config.CHROMA_DIR)
    # start clean so re-running never doubles the collection
    try:
        db.delete_collection(config.COLLECTION_NAME)
    except chromadb.errors.NotFoundError:
        pass
    collection = db.create_collection(
        name=config.COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # so 1 - distance is a real cosine similarity
    )
    collection.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        embeddings=vectors,  # always pass our own vectors, never let Chroma embed
        metadatas=[{"source": c["source"], "page": c["page"]} for c in chunks],
    )
    print(f"Stored {collection.count()} chunks in {config.CHROMA_DIR}/ "
          f"({time.time() - start:.1f}s)")


if __name__ == "__main__":
    main()
