# app/services/response_builder.py

import re


# ---------------------------------------------------
# Extract Recommendations
# ---------------------------------------------------

def extract_recommendations(

    llm_response,

    retrieved_assessments
):

    recommendations = []

    # -----------------------------------
    # Find Structured Recommendation Block
    # -----------------------------------

    marker = "RECOMMENDED_ASSESSMENTS:"

    if marker not in llm_response:

        return recommendations

    recommendation_block = (
        llm_response.split(marker)[-1]
    )

    lines = recommendation_block.split("\n")

    extracted_names = []

    # -----------------------------------
    # Extract Recommendation Names
    # -----------------------------------

    for line in lines:

        line = line.strip()

        if line.startswith("-"):

            assessment_name = (
                line.replace("-", "")
                .strip()
            )

            if assessment_name:

                extracted_names.append(
                    assessment_name
                )

    # -----------------------------------
    # Match Against Retrieved Assessments
    # -----------------------------------

    for extracted_name in extracted_names:

        for assessment in retrieved_assessments:

            catalog_name = assessment.get(
                "name",
                ""
            )

            if not catalog_name:
                continue

            # -----------------------------------
            # Exact Match
            # -----------------------------------

            if (

                catalog_name.lower()
                == extracted_name.lower()

            ):

                test_types = assessment.get(
                    "test_types",
                    []
                )

                # -----------------------------------
                # Extract Test Type
                # -----------------------------------

                if (
                    isinstance(test_types, list)
                    and len(test_types) > 0
                ):

                    first_test_type = (
                        test_types[0]
                    )

                    if isinstance(
                        first_test_type,
                        dict
                    ):

                        test_type = (
                            first_test_type.get(
                                "name",
                                "Unknown"
                            )
                        )

                    else:

                        test_type = str(
                            first_test_type
                        )

                else:

                    test_type = "Unknown"

                recommendations.append({

                    "name": catalog_name,

                    "url": assessment.get(
                        "url",
                        ""
                    ),

                    "test_type": test_type
                })

    return recommendations[:10]


# ---------------------------------------------------
# Clean Reply
# ---------------------------------------------------

def clean_reply(
    llm_response
):

    # -----------------------------------
    # Remove Hidden Recommendation Block
    # -----------------------------------

    marker = "RECOMMENDED_ASSESSMENTS:"

    if marker in llm_response:

        llm_response = (
            llm_response.split(marker)[0]
        )

    # -----------------------------------
    # Remove Excess Newlines
    # -----------------------------------

    reply = re.sub(

        r"\n{3,}",

        "\n\n",

        llm_response
    )

    return reply.strip()


# ---------------------------------------------------
# Determine End Of Conversation
# ---------------------------------------------------

def determine_end_of_conversation(

    conversation_state,

    recommendations
):

    # -----------------------------------
    # No Recommendations Yet
    # -----------------------------------

    if len(recommendations) == 0:

        return False

    # -----------------------------------
    # Latest User Query
    # -----------------------------------

    latest_query = (
        conversation_state.get(
            "latest_user_query",
            ""
        ).lower()
    )

    # -----------------------------------
    # Query Type
    # -----------------------------------

    query_type = (
        conversation_state.get(
            "last_query_type",
            ""
        )
    )

    # -----------------------------------
    # Explicit Completion Signals
    # -----------------------------------

    completion_keywords = [

        "thanks",

        "thank you",

        "perfect",

        "great",

        "looks good",

        "this works",

        "that works",

        "final shortlist",

        "done",

        "that's enough"
    ]

    if any(
        keyword in latest_query
        for keyword in completion_keywords
    ):

        return True

    # -----------------------------------
    # Keep Conversation Open
    # -----------------------------------

    if query_type in [

        "clarification",

        "refinement",

        "comparison"
    ]:

        return False

    # -----------------------------------
    # Default:
    # Recommendations Provided
    # -----------------------------------

    return True


# ---------------------------------------------------
# Build Final Chat Response
# ---------------------------------------------------

def build_chat_response(

    llm_response,

    retrieved_assessments,

    conversation_state
):

    # -----------------------------------
    # Structured Recommendations
    # -----------------------------------

    recommendations = (
        extract_recommendations(

            llm_response,

            retrieved_assessments
        )
    )

    # -----------------------------------
    # User-Visible Reply
    # -----------------------------------

    reply = clean_reply(
        llm_response
    )

    # -----------------------------------
    # Completion Logic
    # -----------------------------------

    end_of_conversation = (
        determine_end_of_conversation(

            conversation_state,

            recommendations
        )
    )

    # -----------------------------------
    # Final Structured API Response
    # -----------------------------------

    final_response = {

        "reply": reply,

        "recommendations":
        recommendations,

        "end_of_conversation":
        end_of_conversation
    }

    return final_response


# ---------------------------------------------------
# Standalone Testing
# ---------------------------------------------------

if __name__ == "__main__":

    sample_llm_response = """

1. OPQ Leadership Report
Why it fits: Executive leadership profiling.
URL: https://example.com/opq

2. Verify G+
Why it fits: Cognitive reasoning.
URL: https://example.com/verify

RECOMMENDED_ASSESSMENTS:
- OPQ Leadership Report
- Verify G+
"""

    sample_assessments = [

        {
            "name":
            "OPQ Leadership Report",

            "url":
            "https://example.com/opq",

            "test_types": [
                {
                    "name":
                    "Personality"
                }
            ]
        },

        {
            "name":
            "Verify G+",

            "url":
            "https://example.com/verify",

            "test_types": [
                {
                    "name":
                    "Cognitive"
                }
            ]
        }
    ]

    sample_state = {

        "latest_user_query":
        "Looks good",

        "last_query_type":
        "recommendation"
    }

    result = build_chat_response(

        sample_llm_response,

        sample_assessments,

        sample_state
    )

    from pprint import pprint

    print("\nFinal Structured Response:\n")

    pprint(result)