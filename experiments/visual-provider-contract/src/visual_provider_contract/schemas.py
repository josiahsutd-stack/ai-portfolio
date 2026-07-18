from __future__ import annotations

from pydantic import BaseModel, Field


class StructuredExtraction(BaseModel):
    detected_objects: list[str] = Field(default_factory=list)
    visible_text: list[str] = Field(default_factory=list)
    defects: list[str] = Field(default_factory=list)
    key_values: dict[str, str] = Field(default_factory=dict)


class VQAResponse(BaseModel):
    answer: str
    structured_json: StructuredExtraction
    confidence: float = Field(ge=0, le=1)
    uncertainty: str
    observations: list[str] = Field(default_factory=list)
    provider: str = "mock"


def validate_image_bytes(image_bytes: bytes) -> str:
    if not image_bytes:
        raise ValueError("Image bytes are empty.")
    signatures = {
        b"\x89PNG\r\n\x1a\n": "png",
        b"\xff\xd8\xff": "jpeg",
        b"GIF87a": "gif",
        b"GIF89a": "gif",
        b"RIFF": "webp_or_riff",
    }
    for signature, image_type in signatures.items():
        if image_bytes.startswith(signature):
            return image_type
    raise ValueError("Unsupported image type. Use PNG, JPEG, GIF, or WebP.")
