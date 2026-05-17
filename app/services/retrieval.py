# app/services/retrieval.py

import json


# ---------------------------------------------------
# Load Processed Catalog
# ---------------------------------------------------

def load_catalog():

    with open(
        "data/processed_catalog.json",
        "r",
        encoding="utf-8"
    ) as file:

        catalog = json.load(
            file
        )

    return catalog


# ---------------------------------------------------
# Simple Semantic Search
# ---------------------------------------------------

def semantic_search(

    query,

    top_k=10
):

    query_lower = query.lower()

    catalog = load_catalog()

    scored_results = []

    for assessment in catalog:

        # ---------------------------------------------------
        # Extract Test Type Information
        # ---------------------------------------------------

        test_types = assessment.get(
            "test_types",
            []
        )

        test_type_codes = " ".join([

            test_type.get(
                "code",
                ""
            )

            for test_type in test_types
        ])

        test_type_names = " ".join([

            test_type.get(
                "name",
                ""
            )

            for test_type in test_types
        ])

        # ---------------------------------------------------
        # Searchable Text
        # ---------------------------------------------------

        searchable_text = " ".join([

            str(
                assessment.get(
                    "search_text",
                    ""
                )
            ),

            str(
                assessment.get(
                    "name",
                    ""
                )
            ),

            str(
                assessment.get(
                    "description",
                    ""
                )
            ),

            " ".join(
                assessment.get(
                    "job_levels",
                    []
                )
            ),

            test_type_codes,

            test_type_names,

            str(
                assessment.get(
                    "duration",
                    ""
                )
            ),

            str(
                assessment.get(
                    "remote",
                    ""
                )
            ),

            str(
                assessment.get(
                    "adaptive",
                    ""
                )
            ),

            " ".join(
                assessment.get(
                    "language",
                    []
                )
            )
        ]).lower()

        # ---------------------------------------------------
        # Keyword Match Scoring
        # ---------------------------------------------------

        score = 0

        query_words = query_lower.split()

        for word in query_words:

            if word in searchable_text:

                score += 1

        scored_results.append({

            "score":
            score,

            "assessment":
            assessment
        })

    # ---------------------------------------------------
    # Sort By Relevance
    # ---------------------------------------------------

    scored_results = sorted(

        scored_results,

        key=lambda x: x["score"],

        reverse=True
    )

    # ---------------------------------------------------
    # Build Structured Results
    # ---------------------------------------------------

    top_results = [

        {

            "id":
            result["assessment"].get(
                "id",
                ""
            ),

            "name":
            result["assessment"].get(
                "name",
                ""
            ),

            "url":
            result["assessment"].get(
                "url",
                ""
            ),

            "description":
            result["assessment"].get(
                "description",
                ""
            ),

            "job_levels":
            result["assessment"].get(
                "job_levels",
                []
            ),

            "test_types":
            result["assessment"].get(
                "test_types",
                []
            ),

            "duration":
            result["assessment"].get(
                "duration",
                ""
            ),

            "remote":
            result["assessment"].get(
                "remote",
                ""
            ),

            "adaptive":
            result["assessment"].get(
                "adaptive",
                ""
            ),

            "language":
            result["assessment"].get(
                "language",
                []
            ),

            "search_text":
            result["assessment"].get(
                "search_text",
                ""
            ),

            "score":
            result["score"]
        }

        for result in scored_results

        if result["score"] > 0
    ]

    return top_results[:top_k]