from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .providers import get_vlm_provider

app = FastAPI(title="Visual QA Provider Contract")


class VQARequest(BaseModel):
    image_base64: str
    question: str


@app.post("/analyze")
def analyze(payload: VQARequest) -> dict[str, object]:
    import base64

    image_bytes = base64.b64decode(payload.image_base64)
    return get_vlm_provider().answer(image_bytes, payload.question).model_dump()
