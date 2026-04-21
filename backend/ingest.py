import sys
from pathlib import Path

import chromadb

sys.path.insert(0, str(Path(__file__).parent))

from rag import (  # noqa: E402
    CHROMA_PATH,
    COLLECTION_NAMES,
    DATA_DIR,
    SOURCE_NAMES,
    chunk_text,
    get_collection,
)


def ingest_property(property_name: str):
    print(f"\nIngesting {property_name} knowledge base...")

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    try:
        client.delete_collection(COLLECTION_NAMES[property_name])
        print(f"  Cleared existing {property_name} collection.")
    except Exception:
        pass

    collection = get_collection(property_name)
    data_dir = DATA_DIR / property_name

    all_chunks: list[str] = []
    all_ids: list[str] = []
    all_metadatas: list[dict] = []
    chunk_id = 0

    for filename, source_name in SOURCE_NAMES[property_name].items():
        filepath = data_dir / filename
        if not filepath.exists():
            print(f"  WARNING: {filename} not found, skipping.")
            continue

        text = filepath.read_text(encoding="utf-8")
        chunks = chunk_text(text, chunk_size=400, overlap=80)
        print(f"  {source_name}: {len(chunks)} chunks")

        for chunk in chunks:
            all_chunks.append(chunk)
            all_ids.append(f"{property_name}_chunk_{chunk_id}")
            all_metadatas.append(
                {
                    "source": source_name,
                    "file": filename,
                    "property": property_name,
                }
            )
            chunk_id += 1

    batch_size = 50
    for index in range(0, len(all_chunks), batch_size):
        collection.add(
            documents=all_chunks[index : index + batch_size],
            ids=all_ids[index : index + batch_size],
            metadatas=all_metadatas[index : index + batch_size],
        )
        print(
            f"  Batch {index // batch_size + 1} ingested "
            f"({len(all_chunks[index : index + batch_size])} chunks)"
        )

    print(f"  Total chunks for {property_name}: {collection.count()}")


if __name__ == "__main__":
    ingest_property("pierre")
    ingest_property("ama")
    print("\nBoth knowledge bases ready.")
