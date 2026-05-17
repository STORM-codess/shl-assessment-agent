import pickle


METADATA_FILE = (
    "data/embeddings/metadata.pkl"
)


def load_metadata():

    with open(
        METADATA_FILE,
        "rb"
    ) as f:

        return pickle.load(f)


def find_assessments_by_name(
    query
):

    metadata = load_metadata()

    query_lower = query.lower()

    matched = []

    for assessment in metadata:

        name = assessment.get(
            "name",
            ""
        ).lower()

        if name in query_lower:

            matched.append(
                assessment
            )

    return matched