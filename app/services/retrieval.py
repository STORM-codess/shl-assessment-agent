# app/services/retrieval.py

import json


# ---------------------------------------------------
# Load Assessment Catalog
# ---------------------------------------------------

def load_catalog():

    with open(
        "C:\Users\ASUS\shl-assessment-agent\data\processed\catalog_processed.json",
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

        searchable_text = " ".join([

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

            str(
                assessment.get(
                    "category",
                    ""
                )
            )
        ]).lower()

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
    # Sort By Score
    # ---------------------------------------------------

    scored_results = sorted(

        scored_results,

        key=lambda x: x["score"],

        reverse=True
    )

    # ---------------------------------------------------
    # Return Structured Top Results
    # ---------------------------------------------------

    top_results = [

        {

            "name":
            result["assessment"].get(
                "name",
                ""
            ),

            "description":
            result["assessment"].get(
                "description",
                ""
            ),

            "category":
            result["assessment"].get(
                "category",
                ""
            ),

            "url":
            result["assessment"].get(
                "url",
                ""
            ),

            "test_type":
            result["assessment"].get(
                "test_type",
                ""
            )
        }

        for result in scored_results

        if result["score"] > 0
    ]

    return top_results[:top_k]