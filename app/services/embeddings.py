import json
import os
import pickle
import numpy as np

_model = None


def get_embedding_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        print("\nLoading embedding model...")
        _model = SentenceTransformer(MODEL_NAME)
        print("Model loaded successfully")

    return _model


# Embedding model
MODEL_NAME = "all-MiniLM-L6-v2"

# File paths
PROCESSED_FILE = "data/processed/catalog_processed.json"

FAISS_INDEX_FILE = "data/embeddings/faiss_index.bin"

METADATA_FILE = "data/embeddings/metadata.pkl"


# NOTE: model and faiss are loaded lazily to avoid import-time errors


def load_catalog():

    with open(PROCESSED_FILE, "r", encoding="utf-8") as f:

        return json.load(f)


def generate_embeddings(catalog):

    search_texts = []

    for item in catalog:

        search_texts.append(
            item["search_text"]
        )

    print("\nGenerating embeddings...")

    model = get_embedding_model()

    embeddings = model.encode(
        search_texts,
        show_progress_bar=True
    )

    return np.array(
        embeddings,
        dtype="float32"
    )


def build_faiss_index(embeddings):

    dimension = embeddings.shape[1]

    print(f"\nEmbedding dimension: {dimension}")
    try:
        import faiss

        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        return index
    except Exception:
        # FAISS not available in this environment
        return None


def save_index(index, catalog):

    os.makedirs(
        "data/embeddings",
        exist_ok=True
    )

    # Save FAISS index
    if index is not None:
        try:
            import faiss

            faiss.write_index(index, FAISS_INDEX_FILE)
            print("\nFAISS index saved successfully")
            print(f"Index file: {FAISS_INDEX_FILE}")
        except Exception:
            print("\nWarning: failed to write FAISS index")

    # Save metadata
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(catalog, f)

    # Also save raw embeddings for environments without FAISS
    try:
        np.save("data/embeddings/embeddings.npy", embeddings_cache)
        print("Embeddings saved to data/embeddings/embeddings.npy")
    except Exception:
        pass

    print(f"Metadata file: {METADATA_FILE}")


if __name__ == "__main__":

    print("\nLoading processed catalog...")

    catalog = load_catalog()

    print(
        f"Loaded {len(catalog)} assessments"
    )

    embeddings = generate_embeddings(catalog)

    print(
        f"\nEmbeddings shape: {embeddings.shape}"
    )

    index = build_faiss_index(embeddings)

    if index is not None:
        print("\nFAISS index built successfully")
    else:
        print("\nFAISS not available; skipping FAISS index build")

    # cache embeddings so save_index can write them even if FAISS missing
    global embeddings_cache
    embeddings_cache = embeddings

    save_index(index, catalog)

    print("\nEmbedding pipeline completed successfully")