from __future__ import annotations

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(doctor|assistant|user|system)$")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    message: ChatMessage
    sources: list[str]
    safety_notice: str
