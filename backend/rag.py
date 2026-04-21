from functools import lru_cache
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions


DATA_DIR = Path(__file__).parent.parent / "data"
CHROMA_PATH = Path(__file__).parent.parent / "chroma_db"

COLLECTION_NAMES = {
    "pierre": "pierre_knowledge",
    "ama": "ama_knowledge",
}

SOURCE_NAMES = {
    "pierre": {
        "pierre_hotel.md": "The Pierre — Hotel Overview",
        "pierre_dining.md": "The Pierre — Dining and F&B",
        "pierre_events.md": "The Pierre — Event Spaces",
        "pierre_policies.md": "The Pierre — Hotel Policies",
        "pierre_faq.md": "The Pierre — FAQ",
        "neighbourhood.md": "Upper East Side Neighbourhood Guide",
    },
    "ama": {
        "ama_overview.md": "ama Stays — Property Overview",
        "ama_guestguide.md": "ama Stays — Guest Guide",
        "ama_local.md": "ama Stays — Local Area Guide",
        "ama_faq.md": "ama Stays — FAQ",
    },
}


@lru_cache(maxsize=1)
def get_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )


def get_collection(property_name: str):
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAMES[property_name],
        embedding_function=get_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    index = 0
    step = max(chunk_size - overlap, 1)

    while index < len(words):
        chunk = " ".join(words[index : index + chunk_size])
        if len(chunk.strip()) > 50:
            chunks.append(chunk)
        index += step

    return chunks


def retrieve(query: str, property_name: str, n_results: int = 5) -> list[dict]:
    collection = get_collection(property_name)
    if collection.count() == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    retrieved: list[dict] = []
    for index, document in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][index]
        retrieved.append(
            {
                "content": document,
                "source": metadata.get("source", "Unknown"),
                "distance": results["distances"][0][index],
            }
        )

    return retrieved


def format_context(retrieved: list[dict]) -> str:
    if not retrieved:
        return "No relevant information found in the knowledge base."

    grouped_sources: dict[str, list[str]] = {}
    for item in retrieved:
        grouped_sources.setdefault(item["source"], []).append(item["content"])

    sections: list[str] = []
    for source, contents in grouped_sources.items():
        sections.append(f"[Source: {source}]\n" + "\n".join(contents))

    return "\n\n---\n\n".join(sections)
