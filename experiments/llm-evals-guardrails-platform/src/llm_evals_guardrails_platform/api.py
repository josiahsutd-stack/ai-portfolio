from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .guardrails import evaluate_case

app = FastAPI(title="Prompt and Output Validation Checks")


class EvalRequest(BaseModel):
    case_id: str
    prompt: str
    output: str
    citations: list[str] = []


@app.post("/evaluate")
def evaluate(payload: EvalRequest) -> dict[str, object]:
    return evaluate_case(
        payload.case_id, payload.prompt, payload.output, payload.citations
    ).to_dict()
