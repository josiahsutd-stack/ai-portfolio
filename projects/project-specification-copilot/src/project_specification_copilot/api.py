from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .engine import SpecificationEngine

app = FastAPI(title="Project Communication and Specification Assistant")


class ConversationMessage(BaseModel):
    role: str
    author: str = "Project participant"
    text: str = Field(min_length=1)


class ConversationRequest(BaseModel):
    messages: list[ConversationMessage]


@app.post("/draft")
def draft_specification(payload: ConversationRequest) -> dict[str, object]:
    engine = SpecificationEngine()
    for message in payload.messages:
        engine.submit_message(message.role, message.text, message.author, data_status="synthetic")
    return {
        "data_status": "synthetic",
        "snapshot": engine.snapshot().to_dict(),
        "draft": engine.draft_specification().to_dict(),
        "boundary": "Deterministic requirement extraction and approval workflow; human review required.",
    }
