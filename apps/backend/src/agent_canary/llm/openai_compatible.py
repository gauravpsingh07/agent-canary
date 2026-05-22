from typing import Any

import httpx

from agent_canary.llm.base import JsonObject, JsonSchema
from agent_canary.llm.exceptions import (
    LLMProviderConfigurationError,
    LLMProviderError,
    LLMProviderResponseError,
)
from agent_canary.llm.parsing import parse_json_object, structured_prompt


class OpenAICompatibleChatProvider:
    def __init__(
        self,
        *,
        provider_name: str,
        api_key: str,
        model_name: str,
        base_url: str,
        timeout_seconds: float = 30.0,
        client: httpx.Client | None = None,
    ) -> None:
        if not api_key:
            raise LLMProviderConfigurationError(f"{provider_name} API key is required")
        if not model_name:
            raise LLMProviderConfigurationError(f"{provider_name} model name is required")

        self._provider_name = provider_name
        self._model_name = model_name
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._client = client or httpx.Client()

    @property
    def provider_name(self) -> str:
        return self._provider_name

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
        payload = {
            "model": self.model_name,
            "messages": self._messages(prompt=prompt, system_prompt=system_prompt),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        data = self._post_chat_completion(payload)
        return self._extract_content(data)

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

    def _post_chat_completion(self, payload: dict[str, Any]) -> JsonObject:
        try:
            response = self._client.post(
                f"{self._base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"{self.provider_name} request failed") from exc

        data = response.json()
        if not isinstance(data, dict):
            raise LLMProviderResponseError(f"{self.provider_name} returned non-object JSON")
        return data

    @staticmethod
    def _messages(prompt: str, system_prompt: str | None) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    def _extract_content(self, data: JsonObject) -> str:
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise LLMProviderResponseError(f"{self.provider_name} returned no choices")

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise LLMProviderResponseError(f"{self.provider_name} choice was malformed")

        message = first_choice.get("message")
        if not isinstance(message, dict):
            raise LLMProviderResponseError(f"{self.provider_name} message was malformed")

        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise LLMProviderResponseError(f"{self.provider_name} returned empty content")
        return content
