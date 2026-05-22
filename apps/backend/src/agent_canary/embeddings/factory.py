from agent_canary.core.config import Settings, get_settings
from agent_canary.embeddings.base import EmbeddingProvider
from agent_canary.embeddings.exceptions import EmbeddingProviderConfigurationError
from agent_canary.embeddings.gemini import GeminiEmbeddingProvider
from agent_canary.embeddings.mock import MockEmbeddingProvider
from agent_canary.embeddings.openai import OpenAIEmbeddingProvider


def build_embedding_provider(settings: Settings | None = None) -> EmbeddingProvider:
    resolved_settings = settings or get_settings()
    provider_name = resolved_settings.embedding_provider.strip().lower()

    if provider_name == "mock":
        return MockEmbeddingProvider(
            model_name=resolved_settings.mock_embedding_model,
            dimensions=resolved_settings.embedding_dimension,
        )

    if provider_name == "gemini":
        return GeminiEmbeddingProvider(
            api_key=resolved_settings.gemini_api_key,
            model_name=resolved_settings.gemini_embedding_model,
            dimensions=resolved_settings.embedding_dimension,
            timeout_seconds=resolved_settings.embedding_timeout_seconds,
        )

    if provider_name == "openai":
        return OpenAIEmbeddingProvider(
            api_key=resolved_settings.openai_api_key,
            model_name=resolved_settings.openai_embedding_model,
            dimensions=resolved_settings.embedding_dimension,
            timeout_seconds=resolved_settings.embedding_timeout_seconds,
        )

    raise EmbeddingProviderConfigurationError(
        f"Unsupported EMBEDDING_PROVIDER '{resolved_settings.embedding_provider}'"
    )
