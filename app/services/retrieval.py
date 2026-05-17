import pickle
from typing import List, Dict, Any


# ---------------------------------------------------
# File Paths
# ---------------------------------------------------

FAISS_INDEX_FILE = "data/embeddings/faiss_index.bin"

METADATA_FILE = "data/embeddings/metadata.pkl"

MODEL_NAME = "all-MiniLM-L6-v2"


# ---------------------------------------------------
# Lazy-loaded model helper
# ---------------------------------------------------

_model = None


def get_embedding_model():
    """
    Return cached embedding model.
    Loads only on first use.
    """

    global _model

    if _model is None:

        from sentence_transformers import (
            SentenceTransformer
        )

        print("\nLoading embedding model...")

        _model = SentenceTransformer(
            MODEL_NAME
        )

        print(
            "Embedding model loaded successfully"
        )

    return _model


# ---------------------------------------------------
# Load FAISS Index + Metadata
# ---------------------------------------------------

def load_index():

    import faiss

    index = faiss.read_index(
        FAISS_INDEX_FILE
    )

    with open(
        METADATA_FILE,
        "rb"
    ) as f:

        metadata = pickle.load(f)

    return index, metadata


# ---------------------------------------------------
# Semantic Search ONLY
# ---------------------------------------------------

def semantic_search(
    query: str,
    top_k: int = 50
) -> List[Dict[str, Any]]:

    index, metadata = load_index()

    print(f"\nQuery: {query}")

    model = get_embedding_model()

    # -----------------------------------
    # Create query embedding
    # -----------------------------------

    query_embedding = model.encode(
        [query]
    )

    query_embedding = np.array(
        query_embedding,
        dtype="float32"
    )

    # -----------------------------------
    # Search FAISS index
    # -----------------------------------

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    seen_names = set()

    # -----------------------------------
    # Build result objects
    # -----------------------------------

    for i in range(top_k):

        idx = indices[0][i]

        if idx == -1:
            continue

        assessment = metadata[idx]

        name = assessment.get(
            "name",
            "Unknown"
        )

        # Avoid duplicates
        if name in seen_names:
            continue

        seen_names.add(name)

        results.append({

            "name": name,

            "url": assessment.get(
                "url",
                ""
            ),

            "description": assessment.get(
                "description",
                ""
            ),

            "distance": float(
                distances[0][i]
            ),

            "test_types": assessment.get(
                "test_types",
                []
            ),

            "remote": assessment.get(
                "remote",
                "unknown"
            ),

            "adaptive": assessment.get(
                "adaptive",
                "unknown"
            ),

            "job_levels": assessment.get(
                "job_levels",
                []
            )
        })

        # Return top 20 unique assessments
        if len(results) >= 20:
            break

    return results


# ---------------------------------------------------
# Pretty Print Results
# ---------------------------------------------------

def display_results(results):

    print("\nTop Matching Assessments:\n")

    for i, result in enumerate(
        results,
        start=1
    ):

        print("=" * 80)

        print(
            f"{i}. {result['name']}"
        )

        print()

        print(
            f"Semantic Distance: "
            f"{result['distance']:.4f}"
        )

        print()

        print(
            f"Remote Testing: "
            f"{result['remote']}"
        )

        print(
            f"Adaptive/IRT: "
            f"{result['adaptive']}"
        )

        print()

        print("Test Types:")

        for test_type in result[
            "test_types"
        ]:

            print(
                f"  - {test_type['name']}"
            )

        print()

        print("Job Levels:")

        for level in result[
            "job_levels"
        ]:

            print(f"  - {level}")

        print()

        print(
            f"URL: "
            f"{result['url']}"
        )

        print()

        description = result[
            "description"
        ]

        if len(description) > 250:

            description = (
                description[:250] + "..."
            )

        print(
            f"Description: "
            f"{description}"
        )

        print("=" * 80)

        print()


# ---------------------------------------------------
# Main
# ---------------------------------------------------

if __name__ == "__main__":

    query = input(
        "\nEnter hiring query: "
    )

    results = semantic_search(query)

    display_results(results)