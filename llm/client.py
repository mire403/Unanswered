from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class LLMConfig:
    model: str = "gpt-4.1-mini"


class LLMClient:
    """
    Thin abstraction over an LLM API.

    This is intentionally minimal and verification-oriented:
    - Always uses system+user prompts.
    - Expects STRICT JSON output and parses it.
    - Raises on malformed responses to avoid silent hallucinations.
    """

    def __init__(self, config: LLMConfig | None = None):
        self.config = config or LLMConfig()

    def _call_raw(self, system_prompt: str, user_prompt: str) -> str:
        """
        Placeholder implementation.

        In production, plug in your LLM provider here (OpenAI, Anthropic, etc.).
        This function must return the raw text content from the model.
        """
        raise NotImplementedError(
            "LLMClient._call_raw must be implemented with a real LLM backend."
        )

    def classify_question(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        raw = self._call_raw(system_prompt, user_prompt)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON from LLM: {raw}") from exc
        return data

    def verify_answer(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        raw = self._call_raw(system_prompt, user_prompt)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON from LLM: {raw}") from exc
        return data

