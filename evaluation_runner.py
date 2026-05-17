# evaluation_runner.py

import json
import time
import requests


# ---------------------------------------------------
# API Configuration
# ---------------------------------------------------

API_URL = "http://127.0.0.1:8000/chat"

TIMEOUT = 60


# ---------------------------------------------------
# Test Cases
# ---------------------------------------------------

test_cases = [

    # ---------------------------------------------------
    # Clarification Required
    # ---------------------------------------------------

    {
        "name":
        "Vague Leadership Query",

        "expected_type":
        "clarification",

        "messages": [

            {
                "role": "user",

                "content":
                "Need leadership test"
            }
        ]
    },

    # ---------------------------------------------------
    # Recommendation Ready
    # ---------------------------------------------------

    {
        "name":
        "Strong Hiring Context",

        "expected_type":
        "recommendation",

        "messages": [

            {
                "role": "user",

                "content":
                "Hiring graduate software engineers for coding and reasoning evaluation"
            }
        ]
    },

    # ---------------------------------------------------
    # Refinement Flow
    # ---------------------------------------------------

    {
        "name":
        "Refinement Add Personality",

        "expected_type":
        "refinement",

        "messages": [

            {
                "role": "user",

                "content":
                "Hiring software engineers for coding assessments"
            },

            {
                "role": "assistant",

                "content":
                """
Here are recommended assessments.

RECOMMENDED_ASSESSMENTS:
- Java Coding Assessment
- Verify Interactive G+
"""
            },

            {
                "role": "user",

                "content":
                "Add personality assessments"
            }
        ]
    },

    # ---------------------------------------------------
    # Comparison Clarification
    # ---------------------------------------------------

    {
        "name":
        "Comparison Acronym Expansion",

        "expected_type":
        "clarification",

        "messages": [

            {
                "role": "user",

                "content":
                "Compare OPQ and GSA"
            }
        ]
    },

    # ---------------------------------------------------
    # Out Of Scope
    # ---------------------------------------------------

    {
        "name":
        "Salary Query Refusal",

        "expected_type":
        "out_of_scope",

        "messages": [

            {
                "role": "user",

                "content":
                "What salary should I pay backend engineers?"
            }
        ]
    },

    # ---------------------------------------------------
    # Healthcare Hiring
    # ---------------------------------------------------

    {
        "name":
        "Healthcare Admin Hiring",

        "expected_type":
        "recommendation",

        "messages": [

            {
                "role": "user",

                "content":
                (
                    "Hiring bilingual healthcare admin staff "
                    "in South Texas for patient record handling "
                    "and HIPAA compliance."
                )
            }
        ]
    },

    # ---------------------------------------------------
    # Leadership Selection
    # ---------------------------------------------------

    {
        "name":
        "Executive Leadership Selection",

        "expected_type":
        "recommendation",

        "messages": [

            {
                "role": "user",

                "content":
                (
                    "Selecting senior executives for leadership "
                    "benchmarking and succession planning with "
                    "focus on strategic decision-making."
                )
            }
        ]
    }
]


# ---------------------------------------------------
# Validate Response Schema
# ---------------------------------------------------

def validate_schema(
    data
):

    required_fields = [

        "reply",

        "recommendations",

        "end_of_conversation"
    ]

    missing_fields = []

    for field in required_fields:

        if field not in data:

            missing_fields.append(
                field
            )

    return {

        "valid":
        len(missing_fields) == 0,

        "missing_fields":
        missing_fields
    }


# ---------------------------------------------------
# Detect Recommendation Block
# ---------------------------------------------------

def has_recommendation_block(
    text
):

    return (
        "RECOMMENDED_ASSESSMENTS:"
        in text
    )


# ---------------------------------------------------
# Detect Clarification Behavior
# ---------------------------------------------------

def looks_like_clarification(
    text
):

    return "?" in text


# ---------------------------------------------------
# Run Single Test
# ---------------------------------------------------

def run_test_case(
    test_case
):

    print("\n" + "=" * 80)

    print(
        f"TEST: "
        f"{test_case['name']}"
    )

    print("=" * 80)

    print("\nExpected Type:")

    print(
        test_case[
            "expected_type"
        ]
    )

    start_time = time.time()

    try:

        response = requests.post(

            API_URL,

            json={
                "messages":
                test_case[
                    "messages"
                ]
            },

            timeout=TIMEOUT
        )

        latency = round(

            time.time() - start_time,

            2
        )

        print(
            f"\nStatus Code: "
            f"{response.status_code}"
        )

        print(
            f"Latency: "
            f"{latency}s"
        )

        # ---------------------------------------------------
        # Parse JSON
        # ---------------------------------------------------

        try:

            data = response.json()

        except Exception:

            print(
                "\nFAILED: Invalid JSON response"
            )

            return

        # ---------------------------------------------------
        # Schema Validation
        # ---------------------------------------------------

        schema_result = validate_schema(
            data
        )

        print("\nSchema Valid:")

        print(
            schema_result["valid"]
        )

        if not schema_result["valid"]:

            print(
                "\nMissing Fields:"
            )

            print(
                schema_result[
                    "missing_fields"
                ]
            )

        # ---------------------------------------------------
        # Extract Reply
        # ---------------------------------------------------

        reply = data.get(
            "reply",
            ""
        )

        print("\nReply:\n")

        print(reply)

        # ---------------------------------------------------
        # Recommendations
        # ---------------------------------------------------

        recommendations = data.get(
            "recommendations",
            []
        )

        print("\nRecommendations:\n")

        print(
            json.dumps(

                recommendations,

                indent=2
            )
        )

        # ---------------------------------------------------
        # End Of Conversation
        # ---------------------------------------------------

        print("\nEnd Of Conversation:")

        print(
            data.get(
                "end_of_conversation"
            )
        )

        # ---------------------------------------------------
        # Behavioral Evaluation
        # ---------------------------------------------------

        print("\nBehavior Checks:\n")

        expected_type = test_case[
            "expected_type"
        ]

        if expected_type == "clarification":

            clarification_detected = (
                looks_like_clarification(
                    reply
                )
            )

            recommendation_detected = (
                has_recommendation_block(
                    reply
                )
            )

            print(
                f"Clarification Detected: "
                f"{clarification_detected}"
            )

            print(
                f"Premature Recommendation: "
                f"{recommendation_detected}"
            )

        elif expected_type in [

            "recommendation",

            "refinement"
        ]:

            recommendation_detected = (
                has_recommendation_block(
                    reply
                )
            )

            print(
                f"Recommendation Block Present: "
                f"{recommendation_detected}"
            )

            print(
                f"Recommendation Count: "
                f"{len(recommendations)}"
            )

        elif expected_type == "comparison":

            print(
                "Comparison behavior manually inspect."
            )

        elif expected_type == "out_of_scope":

            recommendation_detected = (
                has_recommendation_block(
                    reply
                )
            )

            print(
                f"Recommendations Present: "
                f"{recommendation_detected}"
            )

    except Exception as e:

        print("\nFAILED:\n")

        print(str(e))


# ---------------------------------------------------
# Run Full Evaluation
# ---------------------------------------------------

def run_full_evaluation():

    print("\n")

    print("=" * 80)

    print("SHL ASSESSMENT AGENT EVALUATION")

    print("=" * 80)

    for test_case in test_cases:

        run_test_case(
            test_case
        )

    print("\n")

    print("=" * 80)

    print("EVALUATION COMPLETE")

    print("=" * 80)


# ---------------------------------------------------
# Main
# ---------------------------------------------------

if __name__ == "__main__":

    run_full_evaluation()