import json
import os

RAW_FILE = "data/raw/catalog.json"

PROCESSED_FILE = "data/processed/catalog_processed.json"


TEST_TYPE_MAPPING = {
    "Ability & Aptitude": "A",
    "Biodata & Situational Judgment": "B",
    "Competencies": "C",
    "Development & 360": "D",
    "Assessment Exercises": "E",
    "Knowledge & Skills": "K",
    "Personality & Behavior": "P",
    "Simulations": "S"
}


def load_catalog():

    with open(RAW_FILE, "r", encoding="utf-8") as f:

        content = f.read()

        # Remove problematic characters
        content = content.replace("\t", " ")
        content = content.replace("\r", " ")

        return json.loads(content)


def clean_text(text):

    if not text:
        return ""

    return " ".join(str(text).strip().split())


def process_test_types(raw_keys):

    test_types = []

    for key in raw_keys:

        cleaned_key = clean_text(key)

        code = TEST_TYPE_MAPPING.get(cleaned_key)

        if code:

            test_types.append({
                "code": code,
                "name": cleaned_key
            })

    return test_types


def preprocess_assessment(item):

    name = clean_text(item.get("name", ""))

    description = clean_text(item.get("description", ""))

    url = item.get("link", "")

    job_levels = item.get("job_levels", [])

    raw_keys = item.get("keys", [])

    test_types = process_test_types(raw_keys)

    duration = clean_text(item.get("duration", ""))

    remote = item.get("remote", "unknown")

    adaptive = item.get("adaptive", "unknown")

    language = item.get("languages", [])

    # Create test type searchable text
    test_type_text = " ".join([
        f"{t['code']} {t['name']}"
        for t in test_types
    ])

    # Create searchable embedding text
    search_text = f"""
    {name}
    {description}
    {' '.join(job_levels)}
    {test_type_text}
    {duration}
    remote {remote}
    adaptive {adaptive}
    {' '.join(language)}
    """

    processed_item = {
        "search_text": search_text,
        
        "id": item.get("entity_id", ""),

        "name": name,

        "url": url,

        "description": description,

        "job_levels": job_levels,

        "test_types": test_types,

        "duration": duration,

        "remote": remote,

        "adaptive": adaptive,

        "language": language,

        "search_text": clean_text(search_text)
    }

    return processed_item


def preprocess_catalog():

    catalog = load_catalog()

    processed_catalog = []

    for item in catalog:

        if item.get("status") != "ok":
            continue

        processed_item = preprocess_assessment(item)

        processed_catalog.append(processed_item)

    return processed_catalog


def save_processed_catalog(processed_catalog):

    os.makedirs("data/processed", exist_ok=True)

    with open(
        PROCESSED_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            processed_catalog,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"\nSaved {len(processed_catalog)} "
        f"processed assessments"
    )


if __name__ == "__main__":

    processed_catalog = preprocess_catalog()

    print(
        f"\nProcessed assessments: "
        f"{len(processed_catalog)}"
    )

    print("\nSample Processed Assessment:\n")

    print(
        json.dumps(
            processed_catalog[0],
            indent=4,
            ensure_ascii=False
        )
    )

    save_processed_catalog(processed_catalog)