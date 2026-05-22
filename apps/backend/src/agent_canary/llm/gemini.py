from typing import Any

import httpx

from agent_canary.llm.base import JsonObject, JsonSchema
from agent_canary.llm.exceptions import (
    LLMProviderConfigurationError,
    LLMProviderError,
    LLMProviderResponseError,
)
from agent_canary.llm.parsing import parse_json_object, structured_prompt


class GeminiProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        timeout_seconds: float = 30.0,
        client: httpx.Client | None = None,
    ) -> None:
        if not api_key:
            raise LLMProviderConfigurationError("Gemini API key is required")
        if not model_name:
            raise LLMProviderConfigurationError("Gemini model name is required")

        self._api_key = api_key
        self._model_name = model_name
        self._timeout_seconds = timeout_seconds
        self._client = client or httpx.Client()
        self._base_url = "https://generativelanguage.googleapis.com/v1beta"

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> str:
        payload: dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        data = self._post_generate_content(payload)
        return self._extract_text(data)

    def generate_structured(
        self,
        prompt: str,
        system_prompt: str | None,
        schema: JsonSchema,
        temperature: float = 0.0,
    ) -> JsonObject:
        text = self.generate_text(
            prompt=structured_prompt(prompt, schema),
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=1024,
        )
        return parse_json_object(text)

    def _post_generate_content(self, payload: dict[str, Any]) -> JsonObject:
        try:
            response = self._client.post(
                f"{self._base_url}/models/{self.model_name}:generateContent",
                params={"key": self._api_key},
                json=payload,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMProviderError("Gemini request failed") from exc

        data = response.json()
        if not isinstance(data, dict):
            raise LLMProviderResponseError("Gemini returned non-object JSON")
        return data

    def _extract_text(self, data: JsonObject) -> str:
        candidates = data.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            raise LLMProviderResponseError("Gemini returned no candidates")

        first_candidate = candidates[0]
        if not isinstance(first_candidate, dict):
            raise LLMProviderResponseError("Gemini candidate was malformed")

        content = first_candidate.get("content")
        if not isinstance(content, dict):
            raise LLMProviderResponseError("Gemini content was malformed")

        parts = content.get("parts")
        if not isinstance(parts, list):
            raise LLMProviderResponseError("Gemini content parts were malformed")

        text_parts = [part.get("text") for part in parts if isinstance(part, dict)]
        combined = "".join(part for part in text_parts if isinstance(part, str)).strip()
        if not combined:
            raise LLMProviderResponseError("Gemini returned empty text")
        return combined

