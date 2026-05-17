import re


# ---------------------------------------------------
# Extract Recommendation Names
# ---------------------------------------------------

def extract_recommendation_names(
    llm_reply
):

    recommendation_names = []

    lines = llm_reply.split("\n")

    for line in lines:

        line = line.strip()

        # -----------------------------------
        # Match numbered recommendations
        # -----------------------------------

        match = re.match(
            r"^\d+\.\s+(.*)",
            line
        )

        if match:

            recommendation_names.append(
                match.group(1).strip()
            )

        # -----------------------------------
        # Match hyphenated recommendations from
        # a RECOMMENDED_ASSESSMENTS: block
        # -----------------------------------

        if line.startswith("RECOMMENDED_ASSESSMENTS:"):

            # collect subsequent hyphen lines
            continue

        if line.startswith("-"):

            name = line.lstrip("-") .strip()

            if name:

                recommendation_names.append(name)

    return recommendation_names


# ---------------------------------------------------
# Match Recommendations To Catalog Results
# ---------------------------------------------------

def build_recommendations(

    llm_reply,

    retrieved_results
):

    recommendation_names = (
        extract_recommendation_names(
            llm_reply
        )
    )

    recommendations = []

    for result in retrieved_results:

        result_name = result.get(
            "name",
            ""
        )

        # -----------------------------------
        # Match recommendation names
        # -----------------------------------

        for extracted_name in recommendation_names:

            if (
                result_name.lower()
                in extracted_name.lower()
            ):

                # -----------------------------------
                # Extract test type
                # -----------------------------------

                test_type = ""

                test_types = result.get(
                    "test_types",
                    []
                )

                if len(test_types) > 0:

                    first_type = test_types[0]

                    if isinstance(
                        first_type,
                        dict
                    ):

                        test_type = (
                            first_type.get(
                                "code",
                                ""
                            )
                        )

                    else:

                        test_type = str(
                            first_type
                        )

                recommendations.append({

                    "name":
                    result_name,

                    "url":
                    result.get(
                        "url",
                        ""
                    ),

                    "test_type":
                    test_type
                })

                break

    # -----------------------------------
    # Max 10 Recommendations
    # -----------------------------------

    return recommendations[:10]


# ---------------------------------------------------
# Determine Conversation Completion
# ---------------------------------------------------

def determine_end_of_conversation(

    query_type,

    recommendations
):

    # -----------------------------------
    # Clarification Still Ongoing
    # -----------------------------------

    if query_type == "clarification":

        return False

    # -----------------------------------
    # Out Of Scope
    # -----------------------------------

    if query_type == "out_of_scope":

        return True

    # -----------------------------------
    # Recommendations Generated
    # -----------------------------------

    if len(recommendations) > 0:

        return True

    return False


# ---------------------------------------------------
# Build Final API Response
# ---------------------------------------------------

def format_chat_response(

    llm_reply,

    retrieved_results,

    query_type
):

    recommendations = (
        build_recommendations(

            llm_reply,

            retrieved_results
        )
    )

    end_of_conversation = (
        determine_end_of_conversation(

            query_type,

            recommendations
        )
    )

    response = {

        "reply":
        llm_reply,

        "recommendations":
        recommendations,

        "end_of_conversation":
        end_of_conversation
    }

    return response