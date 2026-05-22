from typing import Any

import httpx

from agent_canary.embeddings.exceptions import (
    EmbeddingProviderConfigurationError,
    EmbeddingProviderError,
    EmbeddingProviderResponseError,
)


class OpenAIEmbeddingProvider:
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
            raise EmbeddingProviderConfigurationError("OpenAI API key is required")
        if not model_name:
            raise EmbeddingProviderConfigurationError("OpenAI embedding model is required")

        self._api_key = api_key
        self._model_name = model_name
        self._dimensions = dimensions
        self._timeout_seconds = timeout_seconds
        self._client = client or httpx.Client()

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed_text(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        payload: dict[str, Any] = {"model": self.model_name, "input": texts}
        if self.dimensions > 0:
            payload["dimensions"] = self.dimensions

        try:
            response = self._client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise EmbeddingProviderError("OpenAI embedding request failed") from exc

        data = response.json()
        return extract_openai_embeddings(data)


def extract_openai_embeddings(data: Any) -> list[list[float]]:
    if not isinstance(data, dict):
        raise EmbeddingProviderResponseError("OpenAI returned non-object JSON")
    raw_embeddings = data.get("data")
    if not isinstance(raw_embeddings, list):
        raise EmbeddingProviderResponseError("OpenAI embedding response was malformed")

    sorted_items = sorted(
        (item for item in raw_embeddings if isinstance(item, dict)),
        key=lambda item: int(item.get("index", 0)),
    )
    vectors: list[list[float]] = []
    for item in sorted_items:
        embedding = item.get("embedding")
        if not isinstance(embedding, list):
            raise EmbeddingProviderResponseError("OpenAI embedding item was malformed")
        vectors.append([float(value) for value in embedding])
    if not vectors:
        raise EmbeddingProviderResponseError("OpenAI returned no embeddings")
    return vectors
