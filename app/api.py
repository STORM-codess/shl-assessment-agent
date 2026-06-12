from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (

    ChatRequest,

    ChatResponse
)

from app.services.conversation_state_builder import (
    build_conversation_state
)

from app.services.query_classifier import (
    classify_query
)

from app.services.retrieval import (
    semantic_search
)

from app.services.catalog_lookup import (
    find_assessments_by_name
)

from app.services.llm_recommender import (
    recommend_assessments
)

from app.services.response_formatter import (
    format_chat_response
)


# ---------------------------------------------------
# FastAPI App
# ---------------------------------------------------

app = FastAPI()


# ---------------------------------------------------
# CORS Middleware
# ---------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shl-assesment-frontend.onrender.com"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------
# Health Check
# ---------------------------------------------------

@app.get("/health")
def health_check():

    return {
        "status": "ok"
    }


# ---------------------------------------------------
# Chat Endpoint
# ---------------------------------------------------

@app.post(
    "/chat",
    response_model=ChatResponse
)
def chat_endpoint(
    request: ChatRequest
):

    # -----------------------------------
    # Convert Messages
    # -----------------------------------

    messages = [

        {
            "role": message.role,
            "content": message.content
        }

        for message in request.messages
    ]

    # -----------------------------------
    # Stateless Conversation State
    # -----------------------------------

    conversation_state = (
        build_conversation_state(
            messages
        )
    )

    # -----------------------------------
    # Latest User Query
    # -----------------------------------

    latest_query = conversation_state.get(
        "latest_user_query",
        ""
    )

    # -----------------------------------
    # Query Classification
    # -----------------------------------

    query_type = conversation_state.get(
        "last_query_type",
        classify_query(
            latest_query,
            conversation_state
        )
    )

    # -----------------------------------
    # Retrieval Strategy
    # -----------------------------------

    def build_retrieval_query(
        messages,
        query_type,
        latest_query
    ):

        if query_type == "comparison":
            return latest_query

        user_messages = [
            message["content"]
            for message in messages
            if message["role"] == "user"
        ]

        if user_messages:
            return " ".join(user_messages)

        return latest_query

    retrieval_query = build_retrieval_query(
        messages,
        query_type,
        latest_query
    )

    if query_type == "comparison":

        retrieved_results = (
            find_assessments_by_name(
                latest_query
            )
        )

    else:

        retrieved_results = semantic_search(
            retrieval_query
        )

    # -----------------------------------
    # Mark comparison readiness when enough retrieved results
    # -----------------------------------

    if query_type == "comparison":

        conversation_state["comparison_ready"] = (

            len(retrieved_results) >= 2
        )

    # -----------------------------------
    # LLM Recommendation
    # -----------------------------------

    llm_reply = recommend_assessments(

        latest_query,

        retrieved_results,

        conversation_state,

        query_type
    )

    # -----------------------------------
    # Structured Response
    # -----------------------------------

    response = format_chat_response(

        llm_reply,

        retrieved_results,

        query_type
    )

    return response
