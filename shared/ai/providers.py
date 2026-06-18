from __future__ import annotations

import json
import os
import textwrap
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol


class LLMProvider(Protocol):
    """Small interface used by demos that can work with or without paid APIs."""

    def generate(self, prompt: str, *, system: str | None = None) -> str: ...


@dataclass
class MockLLMProvider:
    """Deterministic local stand-in for an LLM provider."""

    name: str = "mock-local-llm"

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        lines = [line.strip() for line in prompt.splitlines() if line.strip()]
        useful = [
            line for line in lines if len(line) > 35 and not line.lower().startswith("context")
        ]
        summary = " ".join(useful[:3]) or "The available evidence is limited."
        response = textwrap.shorten(summary, width=520, placeholder="...")
        if system:
            return f"{response}\n\nProvider: {self.name}. Grounding: synthetic/demo context."
        return f"{response}\n\nProvider: {self.name}."


@dataclass
class OpenAICompatibleProvider:
    """Minimal OpenAI-compatible chat-completions client using stdlib HTTP."""

    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    timeout_seconds: int = 30

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        url = self.base_url.rstrip("/") + "/chat/completions"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = json.dumps(
            {"model": self.model, "messages": messages, "temperature": 0.2}
        ).encode()
        request = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as exc:
            return MockLLMProvider().generate(
                f"Provider unavailable: {exc}. Fall back to this prompt:\n{prompt}",
                system=system,
            )
        return body["choices"][0]["message"]["content"]


def get_llm_provider() -> LLMProvider:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return MockLLMProvider()
    return OpenAICompatibleProvider(
        api_key=api_key,
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    )
