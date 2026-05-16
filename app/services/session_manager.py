# ---------------------------------------------------
# Simple In-Memory Session Store
# ---------------------------------------------------

session_state = {

    "conversation_history": [],

    "last_user_query": None,

    "last_retrieved_results": [],

    "last_llm_response": None
}


# ---------------------------------------------------
# Add Conversation Message
# ---------------------------------------------------

def add_message(role, content):

    session_state[
        "conversation_history"
    ].append({

        "role": role,

        "content": content
    })


# ---------------------------------------------------
# Save Latest Retrieval
# ---------------------------------------------------

def update_retrieval_results(
    query,
    results
):

    session_state[
        "last_user_query"
    ] = query

    session_state[
        "last_retrieved_results"
    ] = results


# ---------------------------------------------------
# Save Latest LLM Response
# ---------------------------------------------------

def update_llm_response(response):

    session_state[
        "last_llm_response"
    ] = response


# ---------------------------------------------------
# Get Full Session State
# ---------------------------------------------------

def get_session_state():

    return session_state


# ---------------------------------------------------
# Reset Session
# ---------------------------------------------------

def clear_session():

    session_state[
        "conversation_history"
    ] = []

    session_state[
        "last_user_query"
    ] = None

    session_state[
        "last_retrieved_results"
    ] = []

    session_state[
        "last_llm_response"
    ] = None