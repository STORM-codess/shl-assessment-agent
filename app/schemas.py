from typing import List

from pydantic import BaseModel


# ---------------------------------------------------
# Message Schema
# ---------------------------------------------------

class Message(BaseModel):

    role: str

    content: str


# ---------------------------------------------------
# Chat Request Schema
# ---------------------------------------------------

class ChatRequest(BaseModel):

    messages: List[Message]


# ---------------------------------------------------
# Recommendation Schema
# ---------------------------------------------------

class Recommendation(BaseModel):

    name: str

    url: str

    test_type: str


# ---------------------------------------------------
# Chat Response Schema
# ---------------------------------------------------

class ChatResponse(BaseModel):

    reply: str

    recommendations: List[
        Recommendation
    ]

    end_of_conversation: bool