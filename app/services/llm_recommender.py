# app/services/llm_recommender.py

import os
import re

from groq import Groq
from dotenv import load_dotenv

from app.services.context_builder import (
    format_assessment_context
)

from app.services.catalog_lookup import (
    find_assessments_by_name
)


# ---------------------------------------------------
# Load Environment Variables
# ---------------------------------------------------

load_dotenv()


# ---------------------------------------------------
# Configure Groq Client
# ---------------------------------------------------

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ---------------------------------------------------
# Build Conversation History
# ---------------------------------------------------

def build_conversation_history(
    conversation_state
):

    history = ""

    for message in conversation_state.get(
        "conversation_history",
        []
    ):

        role = message.get(
            "role",
            "unknown"
        )

        content = message.get(
            "content",
            ""
        )

        history += (
            f"{role.upper()}: "
            f"{content}\n"
        )

    return history


# ---------------------------------------------------
# Build Clarification Guidance
# ---------------------------------------------------

def build_clarification_guidance(
    conversation_state
):

    coverage = conversation_state.get(
        "context_coverage",
        {}
    )

    clarification_rounds = (
        conversation_state.get(
            "clarification_rounds",
            0
        )
    )

    missing_areas = []

    if not coverage.get(
        "audience_present",
        False
    ):

        missing_areas.append(
            "target audience or role"
        )

    if not coverage.get(
        "purpose_present",
        False
    ):

        missing_areas.append(
            "hiring purpose"
        )

    if not coverage.get(
        "focus_present",
        False
    ):

        missing_areas.append(
            "assessment focus"
        )

    guidance = f"""
Clarification Rounds Already Used:
{clarification_rounds}

Missing Hiring Context:
{', '.join(missing_areas) if missing_areas else 'None'}

Rules:
- Ask ONLY about missing context
- Ask ONE clarification round at a time
- Ask 1 to 2 tightly related questions
- Avoid repeating answered questions
- Avoid overwhelming the user
"""

    return guidance


# ---------------------------------------------------
# Main Recommendation Function
# ---------------------------------------------------

def recommend_assessments(

    query,

    retrieved_assessments,

    conversation_state,

    query_type
):

    # ---------------------------------------------------
    # Safe Copy
    # ---------------------------------------------------

    retrieved_assessments = (
        retrieved_assessments.copy()
    )

    # ---------------------------------------------------
    # Refinement Context Merge
    # ---------------------------------------------------

    if query_type == "refinement":

        prev_recs = conversation_state.get(
            "recommended_assessments",
            []
        )

        existing_names = set(

            [
                a.get("name")
                for a in (
                    retrieved_assessments or []
                )
                if a.get("name")
            ]
        )

        for line in prev_recs:

            name_candidate = re.sub(

                r"^\s*(?:-\s*|\d+\.\s*)",

                "",

                line
            ).strip()

            if not name_candidate:
                continue

            matches = (
                find_assessments_by_name(
                    name_candidate
                )
            )

            if matches:

                for match in matches:

                    match_name = (
                        match.get("name")
                    )

                    if (

                        match_name

                        and match_name
                        not in existing_names

                    ):

                        retrieved_assessments.append(
                            match
                        )

                        existing_names.add(
                            match_name
                        )

                        break

    # ---------------------------------------------------
    # Retrieval Context
    # ---------------------------------------------------

    assessment_text = (
        format_assessment_context(
            retrieved_assessments
        )
    )

    # ---------------------------------------------------
    # Conversation History
    # ---------------------------------------------------

    conversation_history = (
        build_conversation_history(
            conversation_state
        )
    )

    # ---------------------------------------------------
    # Clarification Guidance
    # ---------------------------------------------------

    clarification_guidance = (
        build_clarification_guidance(
            conversation_state
        )
    )

    # ---------------------------------------------------
    # Active Constraints
    # ---------------------------------------------------

    active_constraints = (
        conversation_state.get(
            "active_constraints",
            []
        )
    )

    constraint_text = "\n".join(
        active_constraints
    )

    # ---------------------------------------------------
    # Query-Type Instructions
    # ---------------------------------------------------

    behavior_instruction = ""

    # ---------------------------------------------------
    # Acronym Expansion Enforcement
    # ---------------------------------------------------

    if conversation_state.get(
        "needs_expansion",
        False
    ):

        behavior_instruction = """

The user used an acronym or short form that is not present in the retrieved catalog.

Your task:
- Ask ONE concise clarification question requesting the full form of the acronym.
- Do NOT provide recommendations.
- Do NOT compare assessments.
- Do NOT ask additional questions.

Your response MUST contain ONLY the clarification question.
"""

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "user",
                    "content": (
                        build_conversation_history(
                            conversation_state
                        )
                        + "\n"
                        + behavior_instruction
                    )
                }
            ],

            temperature=0.1
        )

        return response.choices[0].message.content

    # ---------------------------------------------------
    # Clarification Query
    # ---------------------------------------------------

    if query_type == "clarification":

        behavior_instruction = """

The conversation is still missing important hiring information.

Your task:
- Ask ONE clarification round.
- Ask ONLY 1 or 2 tightly related questions.
- Gather missing hiring context efficiently.

DO NOT:
- recommend assessments
- mention assessment names
- suggest products
- ask already answered questions
- overwhelm the user

Your response MUST contain ONLY clarification questions.
"""

    # ---------------------------------------------------
    # Recommendation Query
    # ---------------------------------------------------

    elif query_type == "recommendation":

        behavior_instruction = """

Enough hiring context exists.

Your task:
- Recommend the MOST relevant SHL assessments for the user's hiring scenario.
- Use retrieved catalog data aggressively.
- Prioritize precision over quantity.

IMPORTANT:
Do NOT provide generic recommendations.

You MUST prioritize assessments based on:
1. role alignment
2. seniority alignment
3. assessment focus alignment
4. hiring purpose alignment
5. constraints from conversation history

Examples:
- leadership hiring → leadership/personality assessments
- software engineers → coding/problem-solving assessments
- healthcare admin → compliance/detail-oriented assessments
- graduate hiring → cognitive/entry-level assessments

Recommendation Rules:
- Recommend ONLY genuinely relevant assessments.
- Prefer quality over quantity.
- Avoid redundant assessments with overlapping purpose.
- Default to 3–5 recommendations unless the scenario genuinely requires more.
- Explain WHY each assessment specifically matches the hiring scenario.

For each recommendation include:
1. Assessment Name
2. Why it fits this hiring scenario
3. Key assessment focus

DO NOT generate URLs.

Recommendation tone:
- consultative
- specific
- role-aware
- business-oriented
- non-generic

After recommendations:
- Ask ONE short optional refinement question ONLY if it would meaningfully improve recommendations.

DO NOT:
- ask broad discovery questions
- restart clarification
- recommend irrelevant assessments

VERY IMPORTANT:
At the END of the response,
include this EXACT machine-readable block:

RECOMMENDED_ASSESSMENTS:
- exact assessment name
- exact assessment name
- exact assessment name

Use EXACT catalog assessment names.
"""

    # ---------------------------------------------------
    # Refinement Query
    # ---------------------------------------------------

    elif query_type == "refinement":

        behavior_instruction = """

The user is refining previous recommendations.

Your task:
- Modify the existing shortlist using the user's new constraints.
- Preserve conversational continuity.
- Apply refinement constraints immediately.

Examples:
- add personality assessments
- reduce assessment count
- support remote testing
- focus more on leadership
- remove cognitive testing
- narrow to top 3

IMPORTANT:
Do NOT restart discovery.

You should:
- keep relevant previous recommendations when appropriate
- remove mismatched assessments
- explain WHY recommendations changed

Refinement Rules:
- Prioritize the user's newest constraints.
- Avoid repeating the exact same shortlist unless justified.
- Keep recommendations tightly aligned to the updated request.
- Prefer focused refinement over broad expansion.
- Default to 3–5 recommendations unless user explicitly requests otherwise.

For each recommendation include:
1. Assessment Name
2. Why it fits the UPDATED hiring scenario
3. Key assessment focus

DO NOT generate URLs.

After recommendations:
- Ask ONE short optional follow-up question ONLY if refinement is still ambiguous.

VERY IMPORTANT:
At the END of the response,
include:

RECOMMENDED_ASSESSMENTS:
- exact assessment name
- exact assessment name
"""

    # ---------------------------------------------------
    # Comparison Query
    # ---------------------------------------------------

    elif query_type == "comparison":

        behavior_instruction = """

The user wants assessment comparison.

Your task:
- Compare ONLY using retrieved catalog data.
- DO NOT recommend additional assessments.
- DO NOT include RECOMMENDED_ASSESSMENTS block.
- Avoid bringing in outside knowledge.

If assessment names or retrieved data are unclear,
ask ONE concise clarification question.

Use this structure:

Assessment 1:
- Purpose:
- Focus:
- Target Roles:

Assessment 2:
- Purpose:
- Focus:
- Target Roles:

Key Differences:
- ...

Compare:
- purpose
- assessment focus
- target audience
- job levels
- remote/adaptive support

If catalog information is missing,
say so clearly.
"""

    # ---------------------------------------------------
    # Out Of Scope Query
    # ---------------------------------------------------

    elif query_type == "out_of_scope":

        behavior_instruction = """

The request is outside SHL assessment scope.

Your task:
- Politely refuse.
- Keep the response concise.
- Redirect toward SHL assessment use cases.

DO NOT:
- recommend assessments
- ask follow-up questions
"""

    # ---------------------------------------------------
    # Main Prompt
    # ---------------------------------------------------

    prompt = f"""
You are an expert SHL assessment consultant.

==================================================
PRIMARY OBJECTIVE
==================================================

Your goals:
1. Gather enough hiring context
2. Recommend highly relevant SHL assessments

Avoid:
- generic recommendations
- endless clarification loops
- unnecessary questioning

==================================================
STRICT CLARIFICATION POLICY
==================================================

Ask clarification questions ONLY when essential context is missing.

If conversation already contains:
- audience
- purpose
- assessment focus

recommend immediately.

Maximum clarification rounds:
2

After 2 clarification rounds:
recommend using available context.

==================================================
CLARIFICATION GUIDANCE
==================================================

{clarification_guidance}

==================================================
QUERY TYPE
==================================================

{query_type}

==================================================
QUERY BEHAVIOR
==================================================

{behavior_instruction}

==================================================
CONVERSATION HISTORY
==================================================

{conversation_history}

==================================================
ACTIVE CONSTRAINTS
==================================================

{constraint_text}

==================================================
CURRENT USER QUERY
==================================================

{query}

==================================================
RETRIEVED SHL ASSESSMENTS
==================================================

{assessment_text}

==================================================
GROUNDING RULES
==================================================

1. ONLY use retrieved catalog assessments.

2. NEVER invent:
- assessment names
- URLs
- capabilities
- durations

3. Every recommendation MUST come from catalog data.

==================================================
FINAL RESPONSE STYLE
==================================================

- concise
- executive-ready
- consultative
- grounded
- natural

Respond directly to the user.
"""

    # ---------------------------------------------------
    # Groq Response
    # ---------------------------------------------------

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.1
    )

    return response.choices[0].message.content