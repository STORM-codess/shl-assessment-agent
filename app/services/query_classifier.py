# app/services/query_classifier.py

import re


# ---------------------------------------------------
# Detect Acronyms
# ---------------------------------------------------

def detect_acronyms(
    query
):

    acronyms = re.findall(
        r"\b[A-Z]{2,}\b",
        query
    )

    return acronyms


# ---------------------------------------------------
# Query Classification
# ---------------------------------------------------

def classify_query(
    query,
    session
):

    query_lower = (
        query.lower()
        .strip()
    )

    # ---------------------------------------------------
    # Conversation Context
    # ---------------------------------------------------

    conversation_history = session.get(
        "conversation_history",
        []
    )

    has_previous_context = (
        len(conversation_history) > 1
    )

    # ---------------------------------------------------
    # Comparison Queries
    # ---------------------------------------------------

    comparison_keywords = [

        "compare",

        "difference",

        "vs",

        "versus"
    ]

    if any(
        keyword in query_lower
        for keyword in comparison_keywords
    ):

        acronyms = detect_acronyms(
            query
        )

        # -----------------------------------
        # Require Full Form Expansion
        # -----------------------------------

        if len(acronyms) > 0:

            session[
                "needs_expansion"
            ] = True

            session[
                "unknown_terms"
            ] = acronyms

            return "clarification"

        return "comparison"

    # ---------------------------------------------------
    # Out Of Scope Queries
    # ---------------------------------------------------

    out_of_scope_keywords = [

        "salary",

        "compensation",

        "interview questions",

        "legal advice",

        "labor law",

        "tax",

        "promotion strategy",

        "visa sponsorship",

        "termination policy",

        "offer negotiation",

        "resignation letter",

        "salary negotiation",

        "offer letter"
    ]

    if any(
        keyword in query_lower
        for keyword in out_of_scope_keywords
    ):

        return "out_of_scope"

    # ---------------------------------------------------
    # Refinement Queries
    # ---------------------------------------------------

    refinement_keywords = [

        "add",

        "remove",

        "include",

        "exclude",

        "instead",

        "also",

        "focus more on",

        "less technical",

        "more technical",

        "more leadership",

        "make it",

        "need remote",

        "need adaptive",

        "shorter",

        "longer",

        "top 3",

        "top 2",

        "best 3",

        "best 2",

        "only 3",

        "only 2",

        "which ones",

        "narrow it down",

        "reduce",

        "keep only",

        "replace",

        "swap",

        "change",

        "prioritize"
    ]

    if (

        has_previous_context

        and any(
            keyword in query_lower
            for keyword in refinement_keywords
        )
    ):

        return "refinement"

    # ---------------------------------------------------
    # Explicitly Vague Queries
    # ---------------------------------------------------

    vague_queries = [

        "i need an assessment",

        "recommend assessment",

        "recommend assessments",

        "need tests",

        "need assessment",

        "hiring assessment",

        "suggest assessment",

        "need a solution",

        "we need a solution",

        "help me find",

        "help me select",

        "help us find",

        "solution for",

        "find a solution",

        "we need help",

        "need leadership test",

        "need leadership assessment",

        "leadership test",

        "personality test",

        "need personality test",

        "need cognitive test",

        "coding test",

        "executive assessment",

        "need recommendations"
    ]

    if any(
        vague in query_lower
        for vague in vague_queries
    ):

        return "clarification"

    # ---------------------------------------------------
    # Recommendation Strength Signals
    # ---------------------------------------------------

    recommendation_keywords = [

        # -----------------------------------
        # Roles
        # -----------------------------------

        "engineer",
        "developer",
        "software",
        "backend",
        "frontend",
        "fullstack",
        "architect",
        "manager",
        "leader",
        "leadership",
        "executive",
        "director",
        "cxo",
        "vp",
        "sales",
        "graduate",
        "analyst",
        "consultant",
        "operations",
        "healthcare",
        "admin",

        # -----------------------------------
        # Purpose
        # -----------------------------------

        "selection",
        "development",
        "benchmark",
        "benchmarking",
        "hiring",
        "recruitment",
        "screening",
        "promotion",
        "succession",
        "high-potential",

        # -----------------------------------
        # Focus
        # -----------------------------------

        "coding",
        "reasoning",
        "personality",
        "cognitive",
        "leadership",
        "communication",
        "stakeholder",
        "compliance",
        "problem-solving",
        "decision-making",
        "technical",
        "behavioral",
        "strategic thinking",
        "attention to detail",
        "customer service",
        "hipaa"
    ]

    recommendation_signal_count = sum([

        keyword in query_lower

        for keyword in recommendation_keywords
    ])

    # ---------------------------------------------------
    # Strong Recommendation Query
    # ---------------------------------------------------

    if recommendation_signal_count >= 3:

        return "recommendation"

    # ---------------------------------------------------
    # Very Short Queries
    # Usually Ambiguous
    # ---------------------------------------------------

    word_count = len(
        query_lower.split()
    )

    if word_count <= 5:

        return "clarification"

    # ---------------------------------------------------
    # Fallback
    # ---------------------------------------------------

    return "clarification"


# ---------------------------------------------------
# Standalone Testing
# ---------------------------------------------------

if __name__ == "__main__":

    sample_queries = [

        "Compare OPQ and GSA",

        "Need leadership test",

        "Hiring graduate software engineers for coding and reasoning evaluation",

        "Add personality assessments",

        "What salary should I pay developers?",

        "Need assessments for healthcare admin hiring",

        "Need executive leadership benchmarking assessments"
    ]

    for query in sample_queries:

        session = {

            "conversation_history": [

                {
                    "role": "user",
                    "content": query
                }
            ]
        }

        result = classify_query(
            query,
            session
        )

        print("\nQuery:")
        print(query)

        print("\nClassification:")
        print(result)

        print("\nSession:")
        print(session)

        print("\n" + "=" * 70)