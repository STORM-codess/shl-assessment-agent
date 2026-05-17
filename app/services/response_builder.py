# app/services/response_builder.py

# ---------------------------------------------------
# Extract Recommendation Names
# ---------------------------------------------------

def extract_recommendation_names(
    llm_response
):

    recommendations = []

    marker = "RECOMMENDED_ASSESSMENTS:"

    if marker not in llm_response:

        return recommendations

    recommendation_block = (
        llm_response.split(marker)[-1]
    )

    lines = recommendation_block.split(
        "\n"
    )

    for line in lines:

        line = line.strip()

        if line.startswith("-"):

            recommendation = (
                line.replace("-", "")
                .strip()
            )

            if recommendation:

                recommendations.append(
                    recommendation
                )

    return recommendations


# ---------------------------------------------------
# Clean Assistant Reply
# Remove Machine Block
# ---------------------------------------------------

def clean_reply_text(
    llm_response
):

    marker = "RECOMMENDED_ASSESSMENTS:"

    if marker in llm_response:

        return (
            llm_response.split(marker)[0]
            .strip()
        )

    return llm_response.strip()


# ---------------------------------------------------
# Match Recommendations To Catalog
# ---------------------------------------------------

def match_recommendations_to_catalog(

    recommendation_names,

    retrieved_assessments
):

    matched = []

    seen = set()

    # ---------------------------------------------------
    # Build Catalog Lookup
    # ---------------------------------------------------

    catalog_lookup = {}

    for assessment in retrieved_assessments:

        name = (
            assessment.get(
                "name",
                ""
            )
            .strip()
            .lower()
        )

        if name:

            catalog_lookup[name] = assessment

    # ---------------------------------------------------
    # Exact Matching
    # ---------------------------------------------------

    for recommendation_name in recommendation_names:

        normalized_name = (
            recommendation_name
            .strip()
            .lower()
        )

        if (
            normalized_name
            in catalog_lookup
        ):

            assessment = (
                catalog_lookup[
                    normalized_name
                ]
            )

            assessment_name = (
                assessment.get(
                    "name"
                )
            )

            if (

                assessment_name

                and assessment_name
                not in seen

            ):

                matched.append({

                    "name":
                    assessment.get(
                        "name"
                    ),

                    "url":
                    assessment.get(
                        "url"
                    ),

                    "test_type":
                    assessment.get(
                        "test_type",
                        "Unknown"
                    )
                })

                seen.add(
                    assessment_name
                )

    return matched


# ---------------------------------------------------
# Remove Invalid Recommendations
# ---------------------------------------------------

def filter_valid_recommendations(
    recommendations
):

    filtered = []

    seen = set()

    for recommendation in recommendations:

        name = recommendation.get(
            "name"
        )

        url = recommendation.get(
            "url"
        )

        # -----------------------------------
        # Basic Validation
        # -----------------------------------

        if not name:
            continue

        if not url:
            continue

        # -----------------------------------
        # Duplicate Protection
        # -----------------------------------

        normalized_name = (
            name.lower().strip()
        )

        if normalized_name in seen:
            continue

        seen.add(
            normalized_name
        )

        filtered.append(
            recommendation
        )

    return filtered


# ---------------------------------------------------
# Ensure Recommendation Count
# ---------------------------------------------------

def limit_recommendations(
    recommendations,
    minimum=5,
    maximum=5
):

    # -----------------------------------
    # Remove Empty Entries
    # -----------------------------------

    recommendations = [

        recommendation

        for recommendation in recommendations

        if recommendation.get("name")
    ]

    # -----------------------------------
    # If Fewer Than Minimum
    # Return Whatever Exists
    # -----------------------------------

    if len(recommendations) <= minimum:

        return recommendations

    # -----------------------------------
    # Cap Maximum
    # -----------------------------------

    return recommendations[:maximum]


# ---------------------------------------------------
# Determine End Of Conversation
# ---------------------------------------------------

def determine_end_of_conversation(

    query_type,

    recommendations
):

    # -----------------------------------
    # Clarification Continues Conversation
    # -----------------------------------

    if query_type == "clarification":

        return False

    # -----------------------------------
    # Recommendation Usually Ends
    # -----------------------------------

    if len(recommendations) > 0:

        return True

    # -----------------------------------
    # Out Of Scope
    # -----------------------------------

    if query_type == "out_of_scope":

        return False

    # -----------------------------------
    # Default
    # -----------------------------------

    return False


# ---------------------------------------------------
# Build Final API Response
# ---------------------------------------------------

def build_response(

    llm_response,

    retrieved_assessments,

    query_type
):

    # ---------------------------------------------------
    # Extract Recommendation Names
    # ---------------------------------------------------

    recommendation_names = (
        extract_recommendation_names(
            llm_response
        )
    )

    # ---------------------------------------------------
    # Match Against Catalog
    # ---------------------------------------------------

    recommendations = (
        match_recommendations_to_catalog(

            recommendation_names,

            retrieved_assessments
        )
    )

    # ---------------------------------------------------
    # Final Validation
    # ---------------------------------------------------

    recommendations = (
        filter_valid_recommendations(
            recommendations
        )
    )

    # ---------------------------------------------------
    # Final Recommendation Count
    # ---------------------------------------------------

    recommendations = (
        limit_recommendations(
            recommendations,
            minimum=5,
            maximum=5
        )
    )

    # ---------------------------------------------------
    # Clean Assistant Reply
    # ---------------------------------------------------

    reply = clean_reply_text(
        llm_response
    )

    # ---------------------------------------------------
    # End Of Conversation
    # ---------------------------------------------------

    end_of_conversation = (
        determine_end_of_conversation(

            query_type,

            recommendations
        )
    )

    # ---------------------------------------------------
    # Final API Response
    # ---------------------------------------------------

    response = {

        "reply":
        reply,

        "recommendations":
        recommendations,

        "end_of_conversation":
        end_of_conversation
    }

    return response


# ---------------------------------------------------
# Standalone Testing
# ---------------------------------------------------

if __name__ == "__main__":

    sample_response = """
Here are recommended assessments.

1. OPQ32
Why it fits: Leadership personality assessment.

2. Verify Interactive G+
Why it fits: Cognitive reasoning assessment.

3. Occupational Personality Questionnaire
Why it fits: Behavioral fit analysis.

4. Numerical Reasoning Test
Why it fits: Analytical evaluation.

5. Situational Judgement Test
Why it fits: Decision-making assessment.

RECOMMENDED_ASSESSMENTS:
- OPQ32
- Verify Interactive G+
- Occupational Personality Questionnaire
- Numerical Reasoning Test
- Situational Judgement Test
"""

    sample_catalog = [

        {
            "name":
            "OPQ32",

            "url":
            "https://www.shl.com/opq32",

            "test_type":
            "P"
        },

        {
            "name":
            "Verify Interactive G+",

            "url":
            "https://www.shl.com/verify",

            "test_type":
            "C"
        },

        {
            "name":
            "Occupational Personality Questionnaire",

            "url":
            "https://www.shl.com/opq",

            "test_type":
            "P"
        },

        {
            "name":
            "Numerical Reasoning Test",

            "url":
            "https://www.shl.com/numerical",

            "test_type":
            "C"
        },

        {
            "name":
            "Situational Judgement Test",

            "url":
            "https://www.shl.com/sjt",

            "test_type":
            "B"
        }
    ]

    result = build_response(

        sample_response,

        sample_catalog,

        query_type="recommendation"
    )

    from pprint import pprint

    pprint(result)