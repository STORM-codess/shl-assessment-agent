# app/services/conversation_state_builder.py

from app.services.query_classifier import (
    classify_query
)


# ---------------------------------------------------
# Extract Latest User Query
# ---------------------------------------------------

def get_latest_user_query(
    messages
):

    for message in reversed(messages):

        if message["role"] == "user":

            return message["content"]

    return ""


# ---------------------------------------------------
# Extract Active Constraints
# ---------------------------------------------------

def extract_constraints(
    messages
):

    constraints = []

    refinement_keywords = [

        "add",

        "remove",

        "include",

        "exclude",

        "instead",

        "also",

        "need remote",

        "need adaptive",

        "personality",

        "cognitive",

        "technical",

        "behavioral",

        "leadership",

        "stakeholder",

        "communication",

        "shorter",

        "longer",

        "reduce duration",

        "executive",

        "benchmark",

        "selection",

        "development",

        "top 3",

        "top 2",

        "only 3",

        "focus more on",

        "less technical",

        "more technical"
    ]

    for message in messages:

        if message["role"] != "user":

            continue

        content = (
            message["content"]
            .lower()
        )

        if any(
            keyword in content
            for keyword in refinement_keywords
        ):

            constraints.append(
                message["content"]
            )

    return constraints


# ---------------------------------------------------
# Extract Previous Recommendations
# ---------------------------------------------------

def extract_previous_recommendations(
    messages
):

    recommendations = []

    marker = "RECOMMENDED_ASSESSMENTS:"

    for message in messages:

        if message["role"] != "assistant":

            continue

        content = message[
            "content"
        ]

        if marker not in content:

            continue

        recommendation_block = (
            content.split(marker)[-1]
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
# Has Previous Recommendations
# ---------------------------------------------------

def has_previous_recommendation(
    messages
):

    return len(
        extract_previous_recommendations(
            messages
        )
    ) > 0


# ---------------------------------------------------
# Count Clarification Rounds
# ---------------------------------------------------

def count_clarification_rounds(
    messages
):

    clarification_count = 0

    clarification_keywords = [

        "could you clarify",

        "can you clarify",

        "what level",

        "what roles",

        "selection or development",

        "which competencies",

        "which skills",

        "what kind",

        "are you focusing",

        "is this mainly",

        "who is the target",

        "what is the primary objective",

        "what are you assessing",

        "which capabilities",

        "what audience",

        "what seniority",

        "what focus"
    ]

    for message in messages:

        if message["role"] != "assistant":

            continue

        content = (
            message["content"]
            .lower()
        )

        if any(
            keyword in content
            for keyword in clarification_keywords
        ):

            clarification_count += 1

    return clarification_count


# ---------------------------------------------------
# Detect Context Coverage
# ---------------------------------------------------

def detect_context_coverage(
    messages
):

    full_text = " ".join(

        [
            message["content"].lower()
            for message in messages
        ]
    )

    # ---------------------------------------------------
    # Audience / Role Keywords
    # ---------------------------------------------------

    audience_keywords = [

        # Tech

        "engineer",
        "developer",
        "software",
        "backend",
        "frontend",
        "fullstack",
        "architect",
        "data scientist",
        "analyst",

        # Leadership

        "manager",
        "leader",
        "leadership",
        "executive",
        "director",
        "cxo",
        "vp",

        # Business

        "sales",
        "marketing",
        "consultant",
        "operations",

        # Early Career

        "graduate",
        "intern",
        "entry-level",
        "junior"
    ]

    # ---------------------------------------------------
    # Purpose Keywords
    # ---------------------------------------------------

    purpose_keywords = [

        "selection",

        "development",

        "benchmark",

        "benchmarking",

        "hiring",

        "recruitment",

        "promotion",

        "succession",

        "high-potential",

        "identify",

        "screening"
    ]

    # ---------------------------------------------------
    # Assessment Focus Keywords
    # ---------------------------------------------------

    focus_keywords = [

        "personality",

        "cognitive",

        "technical",

        "leadership",

        "coding",

        "behavioral",

        "reasoning",

        "communication",

        "stakeholder",

        "decision-making",

        "problem-solving",

        "executive fit",

        "strategic thinking",

        "customer service",

        "compliance",

        "attention to detail"
    ]

    audience_present = any(
        keyword in full_text
        for keyword in audience_keywords
    )

    purpose_present = any(
        keyword in full_text
        for keyword in purpose_keywords
    )

    focus_present = any(
        keyword in full_text
        for keyword in focus_keywords
    )

    return {

        "audience_present":
        audience_present,

        "purpose_present":
        purpose_present,

        "focus_present":
        focus_present
    }


# ---------------------------------------------------
# Determine Recommendation Readiness
# ---------------------------------------------------

def determine_recommendation_readiness(

    coverage,

    clarification_rounds
):

    # ---------------------------------------------------
    # Coverage Score
    # ---------------------------------------------------

    context_score = sum([

        coverage["audience_present"],

        coverage["purpose_present"],

        coverage["focus_present"]
    ])

    # ---------------------------------------------------
    # Strong Context
    # ---------------------------------------------------

    if context_score >= 3:

        return True

    # ---------------------------------------------------
    # Practical Recommendation Readiness
    # ---------------------------------------------------

    if (

        context_score >= 2

        and clarification_rounds >= 1

    ):

        return True

    # ---------------------------------------------------
    # Force Recommendation
    # Avoid Endless Clarification
    # ---------------------------------------------------

    if clarification_rounds >= 2:

        return True

    return False


# ---------------------------------------------------
# Build Conversation State
# ---------------------------------------------------

def build_conversation_state(
    messages
):

    # ---------------------------------------------------
    # Latest User Query
    # ---------------------------------------------------

    latest_query = get_latest_user_query(
        messages
    )

    # ---------------------------------------------------
    # Conversation History
    # ---------------------------------------------------

    conversation_history = []

    for message in messages:

        conversation_history.append({

            "role":
            message["role"],

            "content":
            message["content"]
        })

    # ---------------------------------------------------
    # Clarification Tracking
    # ---------------------------------------------------

    clarification_rounds = (
        count_clarification_rounds(
            messages
        )
    )

    # ---------------------------------------------------
    # Context Coverage
    # ---------------------------------------------------

    context_coverage = (
        detect_context_coverage(
            messages
        )
    )

    # ---------------------------------------------------
    # Recommendation Readiness
    # ---------------------------------------------------

    recommendation_ready = (
        determine_recommendation_readiness(

            context_coverage,

            clarification_rounds
        )
    )

    # ---------------------------------------------------
    # Temporary State
    # ---------------------------------------------------

    temp_state = {

        "conversation_history":
        conversation_history,

        "clarification_rounds":
        clarification_rounds,

        "context_coverage":
        context_coverage,

        "recommendation_ready":
        recommendation_ready
    }

    # ---------------------------------------------------
    # Query Classification
    # ---------------------------------------------------

    query_type = classify_query(

        latest_query,

        temp_state
    )

    # ---------------------------------------------------
    # Force Recommendation Override
    # ---------------------------------------------------

    if recommendation_ready:

        query_type = "recommendation"

    # ---------------------------------------------------
    # Conversation Stage
    # ---------------------------------------------------

    if clarification_rounds == 0:

        conversation_stage = "discovery"

    elif recommendation_ready:

        conversation_stage = "recommendation"

    elif has_previous_recommendation(
        messages
    ):

        conversation_stage = "refinement"

    else:

        conversation_stage = "clarification"

    # ---------------------------------------------------
    # Build Final State
    # ---------------------------------------------------

    conversation_state = {

        "conversation_history":
        conversation_history,

        "latest_user_query":
        latest_query,

        "active_constraints":
        extract_constraints(
            messages
        ),

        "recommended_assessments":
        extract_previous_recommendations(
            messages
        ),

        "clarification_rounds":
        clarification_rounds,

        "context_coverage":
        context_coverage,

        "recommendation_ready":
        recommendation_ready,

        "conversation_stage":
        conversation_stage,

        "last_query_type":
        query_type
    }

    return conversation_state


# ---------------------------------------------------
# Standalone Testing
# ---------------------------------------------------

if __name__ == "__main__":

    sample_messages = [

        {
            "role": "user",

            "content":
            "Hiring mid-level backend software engineers "
            "for coding and problem-solving assessment."
        }
    ]

    state = build_conversation_state(
        sample_messages
    )

    print("\nConversation State:\n")

    from pprint import pprint

    pprint(state)