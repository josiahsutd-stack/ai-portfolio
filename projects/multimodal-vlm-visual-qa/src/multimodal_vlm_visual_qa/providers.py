from __future__ import annotations

import base64
import hashlib
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

from .schemas import StructuredExtraction, VQAResponse, validate_image_bytes


def _mime_type(image_type: str) -> str:
    if image_type == "jpeg":
        return "image/jpeg"
    if image_type == "png":
        return "image/png"
    if image_type == "gif":
        return "image/gif"
    if image_type == "webp_or_riff":
        return "image/webp"
    return "application/octet-stream"


def _json_from_text(text: str) -> dict[str, object] | None:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        value = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _response_from_model_text(
    *,
    text: str,
    provider: str,
    image_type: str,
    digest: str,
) -> VQAResponse:
    parsed = _json_from_text(text)
    if not parsed:
        return VQAResponse(
            answer=text.strip() or "The provider returned an empty answer.",
            structured_json=StructuredExtraction(
                detected_objects=[],
                visible_text=[],
                defects=[],
                key_values={
                    "image_fingerprint": digest,
                    "mode": "real_provider_unstructured",
                    "image_type": image_type,
                },
            ),
            confidence=0.5,
            uncertainty="The provider response was not valid structured JSON.",
            observations=["Real provider call completed, but schema parsing fell back to text."],
            provider=provider,
        )

    raw_key_values = parsed.get("key_values", {})
    key_values = raw_key_values if isinstance(raw_key_values, dict) else {}
    extraction = StructuredExtraction(
        detected_objects=[str(item) for item in parsed.get("detected_objects", [])],
        visible_text=[str(item) for item in parsed.get("visible_text", [])],
        defects=[str(item) for item in parsed.get("defects", [])],
        key_values={
            "image_fingerprint": digest,
            "mode": "real_provider",
            "image_type": image_type,
            **{str(key): str(value) for key, value in key_values.items()},
        },
    )
    confidence = parsed.get("confidence", 0.5)
    try:
        confidence_value = max(0.0, min(1.0, float(confidence)))
    except (TypeError, ValueError):
        confidence_value = 0.5
    return VQAResponse(
        answer=str(parsed.get("answer", text.strip())),
        structured_json=extraction,
        confidence=confidence_value,
        uncertainty=str(parsed.get("uncertainty", "No uncertainty statement returned.")),
        observations=[str(item) for item in parsed.get("observations", [])],
        provider=provider,
    )


@dataclass
class MockVLMProvider:
    name: str = "mock-vlm"

    def answer(self, image_bytes: bytes, question: str) -> VQAResponse:
        image_type = validate_image_bytes(image_bytes)
        question_l = question.lower().strip()
        digest = hashlib.sha256(image_bytes[:2048]).hexdigest()[:8]
        extraction = StructuredExtraction(
            detected_objects=["image_region", "visual_layout", image_type],
            visible_text=["synthetic/mock OCR placeholder"] if "text" in question_l else [],
            defects=(
                ["possible surface scratch"]
                if "defect" in question_l or "scratch" in question_l
                else []
            ),
            key_values={"image_fingerprint": digest, "mode": "mock"},
        )
        if "json" in question_l or "extract" in question_l:
            answer = "Structured visual extraction completed in mock mode."
        elif "chart" in question_l or "trend" in question_l:
            answer = "The image appears to contain a visual pattern; mock mode reports a likely upward or highlighted trend if chart elements are present."
        else:
            answer = "Mock VLM analyzed the uploaded image and produced a cautious answer without claiming real visual recognition."
        uncertainty = "Mock mode does not inspect semantic image content; use a real VLM provider for production analysis."
        return VQAResponse(
            answer=answer,
            structured_json=extraction,
            confidence=0.62,
            uncertainty=uncertainty,
            observations=[
                f"Accepted {image_type} image bytes.",
                "Returned schema-constrained output.",
                "Confidence is intentionally conservative in mock mode.",
            ],
            provider=self.name,
        )


@dataclass
class LocalVLMProvider:
    name: str = "local-vlm-interface"

    def answer(self, image_bytes: bytes, question: str) -> VQAResponse:
        return MockVLMProvider(name=self.name).answer(image_bytes, question)


@dataclass
class OpenAICompatibleVLMProvider:
    api_key: str | None = None
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    timeout_seconds: int = 45
    name: str = "openai-compatible-vlm"

    def answer(self, image_bytes: bytes, question: str) -> VQAResponse:
        image_type = validate_image_bytes(image_bytes)
        api_key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return MockVLMProvider(name=f"{self.name}-mock-fallback").answer(image_bytes, question)

        digest = hashlib.sha256(image_bytes[:2048]).hexdigest()[:8]
        data_url = (
            f"data:{_mime_type(image_type)};base64,"
            f"{base64.b64encode(image_bytes).decode('ascii')}"
        )
        system_prompt = (
            "You are a cautious visual QA assistant. Return only JSON with keys: "
            "answer, detected_objects, visible_text, defects, key_values, confidence, "
            "uncertainty, observations. Do not invent details that are not visible."
        )
        payload = json.dumps(
            {
                "model": self.model,
                "temperature": 0.1,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {"type": "image_url", "image_url": {"url": data_url}},
                        ],
                    },
                ],
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            self.base_url.rstrip("/") + "/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
            text = body["choices"][0]["message"]["content"]
        except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as exc:
            fallback = MockVLMProvider(name=f"{self.name}-mock-fallback").answer(
                image_bytes, question
            )
            fallback.observations.append(f"Real provider unavailable: {exc}")
            return fallback
        return _response_from_model_text(
            text=str(text),
            provider=self.name,
            image_type=image_type,
            digest=digest,
        )


def get_vlm_provider() -> MockVLMProvider | LocalVLMProvider | OpenAICompatibleVLMProvider:
    provider = os.getenv("VLM_PROVIDER", "mock").strip().lower()
    if provider in {"openai", "openai-compatible", "hosted"}:
        return OpenAICompatibleVLMProvider(
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        )
    if provider in {"local", "local-vlm"}:
        return LocalVLMProvider()
    return MockVLMProvider()
