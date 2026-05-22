from typing import Any

import httpx

from agent_canary.embeddings.exceptions import (
    EmbeddingProviderConfigurationError,
    EmbeddingProviderError,
    EmbeddingProviderResponseError,
)


class GeminiEmbeddingProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        dimensions: int,
        timeout_seconds: float = 30.0,
        client: httpx.Client | None = None,
    ) -> None:
        if not api_key:
            raise EmbeddingProviderConfigurationError("Gemini API key is required")
        if not model_name:
            raise EmbeddingProviderConfigurationError("Gemini embedding model is required")

        self._api_key = api_key
        self._model_name = model_name
        self._dimensions = dimensions
        self._timeout_seconds = timeout_seconds
        self._client = client or httpx.Client()

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed_text(self, text: str) -> list[float]:
        payload: dict[str, Any] = {"content": {"parts": [{"text": text}]}}
        if self.dimensions > 0:
            payload["output_dimensionality"] = self.dimensions

        try:
            response = self._client.post(
                (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{self.model_name}:embedContent"
                ),
                params={"key": self._api_key},
                json=payload,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise EmbeddingProviderError("Gemini embedding request failed") from exc

        data = response.json()
        return extract_gemini_embedding(data)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(text) for text in texts]


def extract_gemini_embedding(data: Any) -> list[float]:
    if not isinstance(data, dict):
        raise EmbeddingProviderResponseError("Gemini returned non-object JSON")
    embedding = data.get("embedding")
    if not isinstance(embedding, dict):
        raise EmbeddingProviderResponseError("Gemini embedding response was malformed")
    values = embedding.get("values")
    if not isinstance(values, list):
        raise EmbeddingProviderResponseError("Gemini embedding values were missing")
    return [float(value) for value in values]
